from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.responses import response_success
from app.db.session import get_db
from app.repositories.destinations import DestinationRepository
from app.repositories.categories import CategoryRepository
from app.utils.serializers import destination_to_dict, category_to_dict
from app.core.cache import cache_get, cache_set

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/landing")
def landing(request: Request, db: Session = Depends(get_db)):
    cached = cache_get("public:landing")
    if cached:
        return response_success(cached, {"request_id": request.state.request_id})
    destinations = DestinationRepository(db)
    categories = CategoryRepository(db)
    highlights = destinations.top_by_views(limit=6)
    top_ratings = destinations.top_by_rating(limit=6)
    top_favorites = destinations.top_by_favorites(limit=6)
    data = {
        "highlights": [destination_to_dict(d) for d in highlights],
        "categories": [category_to_dict(c) for c in categories.list()],
        "top_ratings": [destination_to_dict(d) for d in top_ratings],
        "top_favorites": [destination_to_dict(d) for d in top_favorites],
    }
    cache_set("public:landing", data)
    return response_success(data, {"request_id": request.state.request_id})
