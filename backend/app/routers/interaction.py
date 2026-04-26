from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.core.responses import response_success
from app.core.deps import get_current_user
from app.db.session import get_db
from app.repositories.interaction import InteractionRepository
from app.services.interaction import InteractionService
from app.schemas.interaction import RatingUpsert
from app.utils.serializers import favorite_to_dict, rating_to_dict, destination_to_dict
from app.core.events import EventType, build_event
from app.core.config import settings
from app.core.kafka_bus import publish_event
from app.clients.internal_http import internal_request_json

router = APIRouter(prefix="/me", tags=["interaction"])


@router.post("/favorites/{destination_id}")
def favorite(destination_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = InteractionService(db)
    fav = service.favorite(current_user.id, destination_id)
    db.commit()
    publish_event(
        settings.kafka_topic_favorite,
        build_event(
            EventType.FAVORITE_CREATED,
            {"user_id": current_user.id, "destination_id": destination_id, "delta": 1},
            request_id=request.state.request_id,
        ),
    )
    return response_success(favorite_to_dict(fav), {"request_id": request.state.request_id})


@router.delete("/favorites/{destination_id}")
def unfavorite(destination_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = InteractionService(db)
    service.unfavorite(current_user.id, destination_id)
    db.commit()
    publish_event(
        settings.kafka_topic_favorite,
        build_event(
            EventType.FAVORITE_DELETED,
            {"user_id": current_user.id, "destination_id": destination_id, "delta": -1},
            request_id=request.state.request_id,
        ),
    )
    return response_success({}, {"request_id": request.state.request_id})


@router.get("/favorites")
def list_favorites(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    offset = (page - 1) * limit
    repo = InteractionRepository(db)
    destination_ids = repo.list_favorite_destination_ids(current_user.id, offset, limit)

    if settings.service_profile == "monolith":
        from app.repositories.destinations import DestinationRepository

        destinations = DestinationRepository(db).get_by_ids(destination_ids)
        data = [destination_to_dict(item) for item in destinations]
    else:
        payload = internal_request_json(
            "POST",
            base_url=settings.destination_service_url,
            path=f"{settings.api_prefix}/internal/destinations/batch",
            json={"ids": destination_ids},
        )
        data = payload.get("data", [])
    meta = {"request_id": request.state.request_id, "page": page, "limit": limit}
    return response_success(data, meta)


@router.put("/ratings/{destination_id}")
def upsert_rating(
    destination_id: int,
    payload: RatingUpsert,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = InteractionService(db)
    old_rating = service.get_rating(current_user.id, destination_id)
    rating = service.upsert_rating(current_user.id, destination_id, payload.rating_score, payload.comment)
    db.commit()
    publish_event(
        settings.kafka_topic_rating,
        build_event(
            EventType.RATING_UPSERTED,
            {
                "user_id": current_user.id,
                "destination_id": destination_id,
                "old_score": old_rating.rating_score if old_rating else None,
                "new_score": payload.rating_score,
            },
            request_id=request.state.request_id,
        ),
    )
    if settings.service_profile != "monolith":
        internal_request_json(
            "POST",
            base_url=settings.destination_service_url,
            path=f"{settings.api_prefix}/internal/destinations/{destination_id}/apply-rating-insight",
            json={
                "new_score": payload.rating_score,
                "new_comment": payload.comment,
                "old_score": old_rating.rating_score if old_rating else None,
                "old_comment": old_rating.comment if old_rating else None,
                "new_review_time": getattr(rating, "updated_at", None),
                "old_review_time": getattr(old_rating, "updated_at", None) if old_rating else None,
                "is_new_rating": old_rating is None,
                "reviewer_user_id": current_user.id,
            },
        )
        internal_request_json(
            "POST",
            base_url=settings.destination_service_url,
            path=f"{settings.api_prefix}/internal/destinations/{destination_id}/recompute-rating-avg",
        )
    return response_success(rating_to_dict(rating), {"request_id": request.state.request_id})


@router.get("/ratings/{destination_id}")
def get_rating(destination_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = InteractionService(db)
    rating = service.get_rating(current_user.id, destination_id)
    if not rating:
        return response_success(None, {"request_id": request.state.request_id})
    return response_success(rating_to_dict(rating), {"request_id": request.state.request_id})
