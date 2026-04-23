import json
import logging
from time import perf_counter

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.responses import response_success
from app.db.session import get_db
from app.services.activity_recommendation import ActivityRecommendationEngine


router = APIRouter(prefix="/public", tags=["public"])
logger = logging.getLogger(__name__)


@router.get("/activities/{activity_slug}/recommendations")
def get_activity_recommendations(
    activity_slug: str,
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    budget_level: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    start = perf_counter()
    fallback_used = False
    engine = ActivityRecommendationEngine(db)
    try:
        data = engine.recommend(activity_slug=activity_slug, page=page, limit=limit, budget_level=budget_level)
        if "error_info" not in data:
            data["error_info"] = None
    except Exception:  # noqa: BLE001
        fallback_used = True
        logger.exception("activity_recommendation.engine_failure")
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

    latency_ms = round((perf_counter() - start) * 1000, 2)
    highlight_count = len(data.get("highlight_destinations") or [])
    recommended_count = len(data.get("recommended_destinations") or [])
    trending_count = len(data.get("trending") or [])
    endpoint_error_code = (data.get("error_info") or {}).get("endpoint_error_code")
    is_empty_result = (highlight_count + recommended_count + trending_count) == 0
    telemetry_payload = {
        "event": "activity_recommendation.telemetry",
        "request_id": request.state.request_id,
        "activity_slug": activity_slug,
        "page": page,
        "limit": limit,
        "budget_level": budget_level,
        "latency_ms": latency_ms,
        "fallback_used": fallback_used,
        "endpoint_error_code": endpoint_error_code,
        "empty_result": is_empty_result,
        "counts": {
            "highlight": highlight_count,
            "recommended": recommended_count,
            "trending": trending_count,
        },
    }
    logger.info(json.dumps(telemetry_payload, ensure_ascii=False))

    return response_success(data, {"request_id": request.state.request_id, "page": page, "limit": limit})