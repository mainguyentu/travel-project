from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.responses import response_success
from app.db.models import Destination, DestinationInsight
from app.db.session import get_db
from app.services.interaction import InteractionService
from app.utils.serializers import destination_to_dict

router = APIRouter(prefix="/internal", tags=["internal"])


def require_internal_key(x_internal_key: str | None = Header(default=None)) -> None:
    if x_internal_key != settings.internal_api_key:
        raise AppError("UNAUTHORIZED", "Invalid internal key", 401)


class BatchRequest(BaseModel):
    ids: list[int] = Field(min_length=1, max_length=100)


@router.get("/destinations/{destination_id}/active")
def destination_active(
    destination_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _key: None = Depends(require_internal_key),
):
    dest = db.get(Destination, destination_id)
    active = bool(dest and dest.status == "active")
    return response_success({"id": destination_id, "active": active}, {"request_id": request.state.request_id})


@router.post("/destinations/batch")
def destinations_batch(
    payload: BatchRequest,
    request: Request,
    db: Session = Depends(get_db),
    _key: None = Depends(require_internal_key),
):
    items = list(
        db.scalars(select(Destination).where(Destination.id.in_(payload.ids), Destination.status == "active")).all()
    )
    return response_success([destination_to_dict(d) for d in items], {"request_id": request.state.request_id})


@router.post("/destinations/{destination_id}/recompute-rating-avg")
def recompute_rating_avg(
    destination_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _key: None = Depends(require_internal_key),
):
    from sqlalchemy import func

    from app.db.models import Rating

    dest = db.get(Destination, destination_id)
    if not dest:
        raise AppError("NOT_FOUND", "Destination not found", 404)
    row = db.execute(
        select(func.count(Rating.rating_score), func.coalesce(func.avg(Rating.rating_score), 0)).where(
            Rating.destination_id == destination_id
        )
    ).one()
    dest.rating_avg = round(float(row[1] or 0), 2)
    db.flush()
    db.commit()
    return response_success(
        {"id": dest.id, "rating_avg": float(dest.rating_avg), "rating_count": int(row[0] or 0)},
        {"request_id": request.state.request_id},
    )


@router.post("/destinations/{destination_id}/apply-rating-insight")
def apply_rating_insight(
    destination_id: int,
    request: Request,
    db: Session = Depends(get_db),
    _key: None = Depends(require_internal_key),
):
    service = InteractionService(db)
    dest = db.get(Destination, destination_id)
    if not dest:
        raise AppError("NOT_FOUND", "Destination not found", 404)
    service._recompute_avg(destination_id)
    insight = db.get(DestinationInsight, destination_id)
    data = {"rating_avg": float(dest.rating_avg), "status": "ok"}
    if insight:
        insight.final_data = {**(insight.final_data or {}), **data}
    else:
        db.add(DestinationInsight(destination_id=destination_id, final_data=data))
    db.commit()
    return response_success({"id": destination_id, **data}, {"request_id": request.state.request_id})
