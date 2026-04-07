from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.core.responses import response_success
from app.db.session import get_db
from app.repositories.destinations import DestinationRepository
from app.services.destinations import DestinationService
from app.utils.serializers import destination_to_dict
from app.core.cache import cache_get, cache_set, key_dest_list, key_dest_detail
from app.core.config import settings
from app.core.events import EventType, build_event
from app.core.kafka_bus import publish_event
from app.core.search import search_destination_ids

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
    offset = (page - 1) * limit
    repo = DestinationRepository(db)
    cache_key = key_dest_list(category_slug, price_level, rating_min, page, sort, keyword)
    cached = cache_get(cache_key)
    if cached:
        data = cached.get("data", [])
        total = cached.get("total", 0)
        meta = {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total}
        return response_success(data, meta)
    items = repo.list(category_slug, price_level, rating_min, keyword, sort, offset, limit)
    total = repo.count(category_slug, price_level, rating_min, keyword)
    data = [destination_to_dict(d) for d in items]
    cache_set(cache_key, {"data": data, "total": total})
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
    items = None

    if settings.search_use_elasticsearch and q:
        ids = search_destination_ids(q=q, category_slug=category_slug, price_level=price_level, page=page, limit=limit)
        if ids is not None:
            items = repo.get_by_ids(ids)

    if items is None:
        items = repo.search(q, category_slug, price_level, offset, limit)

    data = [destination_to_dict(d) for d in items]
    meta = {"request_id": request.state.request_id, "page": page, "limit": limit}
    return response_success(data, meta)


@router.get("/{destination_id}")
def detail(destination_id: int, request: Request, db: Session = Depends(get_db)):
    cache_key = key_dest_detail(destination_id)
    cached = cache_get(cache_key)
    if cached:
        if "insight" not in cached or "metrics" not in cached:
            service = DestinationService(db)
            destination = service.get_detail(destination_id, increment_view=False)
            cached = destination_to_dict(destination)
        repo = DestinationRepository(db)
        repo.increment_view(destination_id)
        db.commit()
        publish_event(
            settings.kafka_topic_view,
            build_event(
                EventType.DESTINATION_VIEWED,
                {"destination_id": destination_id, "delta": 1},
                request_id=request.state.request_id,
            ),
        )
        cached["view_count"] = int(cached.get("view_count", 0)) + 1
        cache_set(cache_key, cached)
        return response_success(cached, {"request_id": request.state.request_id})
    service = DestinationService(db)
    destination = service.get_detail(destination_id, increment_view=True)
    db.commit()
    publish_event(
        settings.kafka_topic_view,
        build_event(
            EventType.DESTINATION_VIEWED,
            {"destination_id": destination_id, "delta": 1},
            request_id=request.state.request_id,
        ),
    )
    data = destination_to_dict(destination)
    cache_set(cache_key, data)
    return response_success(data, {"request_id": request.state.request_id})
