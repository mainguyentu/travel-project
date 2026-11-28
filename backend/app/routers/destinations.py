from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session

from app.core.deps import get_optional_user_id
from app.core.errors import AppError
from app.core.responses import response_success
from app.db.session import get_db
from app.repositories.destinations import DestinationRepository
from app.services import events as event_bus
from app.services import search as search_svc
from app.utils.serializers import category_to_dict, destination_to_dict

router = APIRouter(prefix="/destinations", tags=["destinations"])


@router.get("")
def list_destinations(
    request: Request,
    category_slug: str | None = None,
    price_level: str | None = None,
    rating_min: float | None = None,
    keyword: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    sort: str | None = None,
    db: Session = Depends(get_db),
):
    if price_level and price_level not in ("free", "low", "medium", "high"):
        raise AppError("VALIDATION_ERROR", "Invalid price_level", 400)
    if sort and sort not in ("rating", "views", "name", "latest"):
        raise AppError("VALIDATION_ERROR", "Invalid sort", 400)
    offset = (page - 1) * limit
    repo = DestinationRepository(db)
    items = repo.list(category_slug, price_level, rating_min, keyword, sort, offset, limit)
    total = repo.count(category_slug, price_level, rating_min, keyword)
    data = [destination_to_dict(d) for d in items]
    meta = {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total}
    return response_success(data, meta)


@router.get("/search")
def search(
    request: Request,
    q: str = "",
    category_slug: str | None = None,
    price_level: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * limit
    repo = DestinationRepository(db)
    ids, es_used = search_svc.search_ids(q, category_slug, price_level, offset, limit)
    if es_used:
        items = repo.get_by_ids(ids)
        by_id = {d.id: d for d in items}
        items = [by_id[i] for i in ids if i in by_id]
    else:
        items = repo.search(q, category_slug, price_level, offset, limit)
    data = [destination_to_dict(d) for d in items]
    meta = {"request_id": request.state.request_id, "page": page, "limit": limit, "q": q,
            "search_engine": "elasticsearch" if es_used else "db"}
    return response_success(data, meta)


@router.get("/{destination_id}")
def detail(destination_id: int, request: Request, db: Session = Depends(get_db)):
    repo = DestinationRepository(db)
    destination = repo.get_detail(destination_id)
    if not destination or destination.status != "active":
        raise AppError("NOT_FOUND", "Destination not found", 404)
    repo.increment_view(destination_id)
    try:
        repo.record_user_view(get_optional_user_id(request), destination_id)
    except Exception:
        pass
    db.commit()
    db.refresh(destination)
    event_bus.publish("destination.viewed", {"destination_id": destination_id})
    insight_row = repo.insight_for(destination_id)
    fav_count = repo.favorite_count(destination_id)
    rating_count, rating_sum = repo.rating_stats(destination_id)
    cats = repo.categories_for(destination_id)
    data = destination_to_dict(
        destination,
        categories=cats,
        insight=insight_row.final_data if insight_row else None,
        favorite_count=fav_count,
        rating_count=rating_count,
        rating_sum=rating_sum,
    )
    return response_success(data, {"request_id": request.state.request_id})
