from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.responses import response_success
from app.db.session import get_db
from app.repositories.destinations import DestinationRepository
from app.schemas.internal import IdsRequest, ApplyRatingInsightRequest
from app.services.insight import InsightService
from app.core.cache import invalidate_admin_stats_cache, invalidate_destination_cache, invalidate_public_landing_cache


router = APIRouter(prefix="/internal/destinations", tags=["internal-destination"])


@router.get("/{destination_id}/active")
def assert_active(destination_id: int, db: Session = Depends(get_db)):
    destination = DestinationRepository(db).get_by_id(destination_id)
    if not destination or destination.status != "active":
        raise AppError("NOT_FOUND", "Destination not found", status_code=404)
    return response_success({"destination_id": destination_id})


@router.post("/batch")
def batch_get(payload: IdsRequest, db: Session = Depends(get_db)):
    repo = DestinationRepository(db)
    items = repo.get_by_ids(payload.ids)
    from app.utils.serializers import destination_to_dict

    data = [destination_to_dict(item) for item in items]
    return response_success(data)


@router.post("/{destination_id}/apply-rating-insight")
def apply_rating_insight(destination_id: int, payload: ApplyRatingInsightRequest, db: Session = Depends(get_db)):
    service = InsightService(db)
    service.apply_rating_update(
        destination_id=destination_id,
        new_score=payload.new_score,
        new_comment=payload.new_comment,
        old_score=payload.old_score,
        old_comment=payload.old_comment,
        new_review_time=payload.new_review_time,
        old_review_time=payload.old_review_time,
        is_new_rating=payload.is_new_rating,
        reviewer_user_id=payload.reviewer_user_id,
    )
    db.commit()
    invalidate_destination_cache(destination_id)
    invalidate_public_landing_cache()
    return response_success({})


@router.post("/{destination_id}/recompute-rating-avg")
def recompute_rating_avg(destination_id: int, db: Session = Depends(get_db)):
    DestinationRepository(db).recompute_rating_avg(destination_id)
    db.commit()
    invalidate_destination_cache(destination_id)
    invalidate_admin_stats_cache()
    invalidate_public_landing_cache()
    return response_success({})
