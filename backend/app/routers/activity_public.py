from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import response_success
from app.db.session import get_db
from app.services.activity_recommendation import ActivityRecommendationEngine


router = APIRouter(prefix="/public", tags=["public"])


@router.get("/activities/{activity_slug}/recommendations")
def get_activity_recommendations(
    activity_slug: str,
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    budget_level: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    engine = ActivityRecommendationEngine(db)
    try:
        data = engine.recommend(activity_slug=activity_slug, page=page, limit=limit, budget_level=budget_level)
        if "error_info" not in data:
            data["error_info"] = None
    except Exception:  # noqa: BLE001
        data = {
            "activity": None,
            "highlight_destinations": [],
            "recommended_destinations": [],
            "trending": [],
            "error_info": {
                "endpoint_error_code": "ACTIVITY_RECOMMENDATION_ENDPOINT_ERROR",
                "endpoint_error_message": "Failed to compute recommendations",
            },
        }
    return response_success(data, {"request_id": request.state.request_id, "page": page, "limit": limit})