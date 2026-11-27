from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import AppError
from app.core.responses import response_success
from app.db.models import Category
from app.db.session import get_db
from app.repositories.destinations import DestinationRepository
from app.utils.serializers import category_to_dict, destination_to_dict

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/activities/{slug}/recommendations")
def activity_recommendations(
    slug: str,
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    budget_level: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if not settings.activity_recommendation_enabled:
        raise AppError("ACTIVITY_RECOMMENDATION_ENDPOINT_ERROR", "Activity recommendations disabled", 503)
    cat = db.scalar(select(Category).where(Category.slug == slug))
    if not cat:
        raise AppError("NOT_FOUND", "Activity not found", 404)
    repo = DestinationRepository(db)
    offset = (page - 1) * limit
    price = budget_level if budget_level in ("free", "low", "medium", "high") else None
    items = repo.list(slug, price, None, None, "rating", offset, limit)
    total = repo.count(slug, price, None, None)
    highlights = repo.top_views(3)
    data = {
        "activity": category_to_dict(cat),
        "highlight_destinations": [destination_to_dict(d) for d in highlights],
        "recommended_destinations": [destination_to_dict(d) for d in items],
        "trending": [destination_to_dict(d) for d in repo.top_favorites(3)],
        "error_info": None,
    }
    return response_success(
        data, {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total}
    )
