from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.core.errors import AppError
from app.core.events import EventType, build_event
from app.core.kafka_bus import publish_event
from app.core.responses import response_success
from app.core.config import settings
from app.db.session import get_db
from app.repositories.categories import CategoryRepository
from app.repositories.destinations import DestinationRepository
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.destination import DestinationBulkCreate, DestinationCreate, DestinationUpdate
from app.services.destinations import DestinationService
from app.utils.serializers import category_to_dict, destination_to_dict
from app.core.cache import invalidate_list_cache, invalidate_public_landing_cache


router = APIRouter(
    prefix="/internal/admin",
    tags=["internal-destination-admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/categories")
def list_categories(request: Request, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    data = [category_to_dict(c) for c in repo.list()]
    return response_success(data, {"request_id": request.state.request_id})


@router.post("/categories", status_code=201)
def create_category(payload: CategoryCreate, request: Request, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    if repo.get_by_slug(payload.slug):
        raise AppError("CONFLICT", "Slug already exists", status_code=409)
    category = repo.create(payload.name, payload.slug, payload.descriptions)
    db.commit()
    invalidate_list_cache()
    invalidate_public_landing_cache()
    return response_success(category_to_dict(category), {"request_id": request.state.request_id})


@router.put("/categories/{category_id}")
def update_category(category_id: int, payload: CategoryUpdate, request: Request, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    category = repo.get_by_id(category_id)
    if not category:
        raise AppError("NOT_FOUND", "Category not found", status_code=404)
    if payload.slug:
        existing = repo.get_by_slug(payload.slug)
        if existing and existing.id != category_id:
            raise AppError("CONFLICT", "Slug already exists", status_code=409)
    category = repo.update(category, payload.model_dump(exclude_unset=True))
    db.commit()
    invalidate_list_cache()
    invalidate_public_landing_cache()
    return response_success(category_to_dict(category), {"request_id": request.state.request_id})


@router.delete("/categories/{category_id}")
def delete_category(category_id: int, request: Request, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    category = repo.get_by_id(category_id)
    if category:
        repo.delete(category)
        db.commit()
        invalidate_list_cache()
        invalidate_public_landing_cache()
    return response_success({}, {"request_id": request.state.request_id})


@router.get("/destinations")
def list_destinations(
    request: Request,
    status: str | None = None,
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * limit
    repo = DestinationRepository(db)
    items = repo.list_admin(status, keyword, offset, limit)
    total = repo.count_admin(status, keyword)
    data = [destination_to_dict(d) for d in items]
    meta = {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total}
    return response_success(data, meta)


@router.post("/destinations", status_code=201)
def create_destination(payload: DestinationCreate, request: Request, db: Session = Depends(get_db)):
    service = DestinationService(db)
    data = payload.model_dump(exclude={"category_ids"})
    destination = service.create(data, payload.category_ids)
    db.commit()
    publish_event(
        settings.kafka_topic_destination,
        build_event(
            EventType.DESTINATION_CREATED,
            {"destination": destination_to_dict(destination)},
            request_id=request.state.request_id,
        ),
    )
    return response_success(destination_to_dict(destination), {"request_id": request.state.request_id})


@router.post("/destinations/bulk", status_code=201)
def create_destinations_bulk(payload: DestinationBulkCreate, request: Request, db: Session = Depends(get_db)):
    service = DestinationService(db)
    destinations_payload = [item.model_dump(exclude={"category_ids"}) | {"category_ids": item.category_ids} for item in payload.destinations]
    destinations = service.create_many(destinations_payload)
    db.commit()
    publish_event(
        settings.kafka_topic_destination,
        build_event(
            EventType.DESTINATION_CREATED,
            {"destinations": [destination_to_dict(destination) for destination in destinations]},
            request_id=request.state.request_id,
        ),
    )
    data = [destination_to_dict(destination) for destination in destinations]
    return response_success(data, {"request_id": request.state.request_id, "count": len(data)})


@router.put("/destinations/{destination_id}")
def update_destination(destination_id: int, payload: DestinationUpdate, request: Request, db: Session = Depends(get_db)):
    service = DestinationService(db)
    data = payload.model_dump(exclude_unset=True, exclude={"category_ids"})
    destination = service.update(destination_id, data, payload.category_ids)
    db.commit()
    publish_event(
        settings.kafka_topic_destination,
        build_event(
            EventType.DESTINATION_UPDATED,
            {"destination": destination_to_dict(destination)},
            request_id=request.state.request_id,
        ),
    )
    return response_success(destination_to_dict(destination), {"request_id": request.state.request_id})


@router.delete("/destinations/{destination_id}")
def delete_destination(destination_id: int, request: Request, db: Session = Depends(get_db)):
    service = DestinationService(db)
    service.delete(destination_id)
    db.commit()
    publish_event(
        settings.kafka_topic_destination,
        build_event(
            EventType.DESTINATION_DELETED,
            {"destination_id": destination_id},
            request_id=request.state.request_id,
        ),
    )
    return response_success({}, {"request_id": request.state.request_id})

