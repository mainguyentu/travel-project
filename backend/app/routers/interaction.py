from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.core.responses import response_success
from app.core.deps import get_current_user
from app.db.session import get_db
from app.repositories.interaction import InteractionRepository
from app.services.interaction import InteractionService
from app.schemas.interaction import RatingUpsert
from app.utils.serializers import favorite_to_dict, rating_to_dict, destination_to_dict

router = APIRouter(prefix="/me", tags=["interaction"])


@router.post("/favorites/{destination_id}")
def favorite(destination_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = InteractionService(db)
    fav = service.favorite(current_user.id, destination_id)
    db.commit()
    return response_success(favorite_to_dict(fav), {"request_id": request.state.request_id})


@router.delete("/favorites/{destination_id}")
def unfavorite(destination_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = InteractionService(db)
    service.unfavorite(current_user.id, destination_id)
    db.commit()
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
    items = repo.list_favorites(current_user.id, offset, limit)
    data = [destination_to_dict(i) for i in items]
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
    rating = service.upsert_rating(current_user.id, destination_id, payload.rating_score, payload.comment)
    db.commit()
    return response_success(rating_to_dict(rating), {"request_id": request.state.request_id})


@router.get("/ratings/{destination_id}")
def get_rating(destination_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = InteractionService(db)
    rating = service.get_rating(current_user.id, destination_id)
    if not rating:
        return response_success(None, {"request_id": request.state.request_id})
    return response_success(rating_to_dict(rating), {"request_id": request.state.request_id})
