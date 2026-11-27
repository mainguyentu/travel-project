from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.core.responses import response_success
from app.db.session import get_db
from app.repositories.destinations import DestinationRepository
from app.utils.serializers import destination_to_dict

router = APIRouter(prefix="/analytics", tags=["analytics"], dependencies=[Depends(require_admin)])


def _parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@router.get("/summary")
def summary(request: Request, db: Session = Depends(get_db)):
    repo = DestinationRepository(db)
    data = {
        "total_destinations": repo.count(),
        "top_favorites": [destination_to_dict(d) for d in repo.top_favorites(5)],
        "top_ratings": [destination_to_dict(d) for d in repo.top_ratings(5)],
        "top_views": [destination_to_dict(d) for d in repo.top_views(5)],
    }
    return response_success(data, {"request_id": request.state.request_id})


@router.get("/top-favorites")
def top_favorites(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
):
    repo = DestinationRepository(db)
    items = repo.top_favorites(limit, _parse_dt(from_date), _parse_dt(to_date))
    return response_success([destination_to_dict(d) for d in items], {"request_id": request.state.request_id})


@router.get("/top-ratings")
def top_ratings(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
):
    repo = DestinationRepository(db)
    items = repo.top_ratings(limit, _parse_dt(from_date), _parse_dt(to_date))
    return response_success([destination_to_dict(d) for d in items], {"request_id": request.state.request_id})


@router.get("/top-views")
def top_views(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    repo = DestinationRepository(db)
    return response_success(
        [destination_to_dict(d) for d in repo.top_views(limit)], {"request_id": request.state.request_id}
    )
