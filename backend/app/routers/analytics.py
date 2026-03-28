from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import response_success
from app.db.session import get_db
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def summary(request: Request, db: Session = Depends(get_db)):
    service = AnalyticsService(db)
    return response_success(service.summary(), {"request_id": request.state.request_id})


@router.get("/top-favorites")
def top_favorites(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    return response_success(service.top_favorites(limit), {"request_id": request.state.request_id, "limit": limit})


@router.get("/top-ratings")
def top_ratings(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    return response_success(service.top_ratings(limit), {"request_id": request.state.request_id, "limit": limit})


@router.get("/top-views")
def top_views(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = AnalyticsService(db)
    return response_success(service.top_views(limit), {"request_id": request.state.request_id, "limit": limit})
