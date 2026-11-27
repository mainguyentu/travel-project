from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import response_success
from app.db.session import get_db
from app.repositories.destinations import DestinationRepository
from app.utils.serializers import category_to_dict, destination_to_dict

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/landing")
def landing(request: Request, db: Session = Depends(get_db)):
    repo = DestinationRepository(db)
    highlights = repo.top_views(limit=6)
    categories = repo.categories_with_counts()
    top_ratings = repo.top_ratings(limit=6)
    top_favorites = repo.top_favorites(limit=6)
    data = {
        "highlights": [destination_to_dict(d) for d in highlights],
        "categories": [category_to_dict(c, count) for c, count in [(r["category"], r["count"]) for r in categories]],
        "top_ratings": [destination_to_dict(d) for d in top_ratings],
        "top_favorites": [destination_to_dict(d) for d in top_favorites],
    }
    return response_success(data, {"request_id": request.state.request_id})
