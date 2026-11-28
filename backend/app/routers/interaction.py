from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.responses import response_success
from app.db.session import get_db
from app.repositories.destinations import DestinationRepository
from app.schemas.interaction import RatingUpsert
from app.services.interaction import InteractionService
from app.utils.serializers import destination_to_dict
from app.services import events as event_bus

router = APIRouter(prefix="/me", tags=["interaction"])


@router.post("/favorites/{destination_id}")
def favorite(destination_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = InteractionService(db)
    fav = service.favorite(current_user.id, destination_id)
    db.commit()
    event_bus.publish("favorite.added", {"destination_id": destination_id, "user_id": current_user.id})
    return response_success(
        {"user_id": fav.user_id, "destination_id": fav.destination_id},
        {"request_id": request.state.request_id},
    )


@router.delete("/favorites/{destination_id}")
def unfavorite(destination_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = InteractionService(db)
    service.unfavorite(current_user.id, destination_id)
    db.commit()
    event_bus.publish("favorite.removed", {"destination_id": destination_id, "user_id": current_user.id})
    return response_success({}, {"request_id": request.state.request_id})


@router.get("/favorites")
def list_favorites(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = InteractionService(db)
    ids = service.list_favorite_ids(current_user.id, (page - 1) * limit, limit)
    repo = DestinationRepository(db)
    data = [destination_to_dict(d) for d in repo.get_by_ids(ids)]
    return response_success(data, {"request_id": request.state.request_id, "page": page, "limit": limit})


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
    event_bus.publish("rating.upserted", {"destination_id": destination_id, "user_id": current_user.id,
                                          "rating_score": payload.rating_score})
    return response_success(
        {"destination_id": rating.destination_id, "rating_score": rating.rating_score, "comment": rating.comment},
        {"request_id": request.state.request_id},
    )


@router.get("/ratings/{destination_id}")
def get_rating(destination_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    service = InteractionService(db)
    rating = service.get_rating(current_user.id, destination_id)
    data = None if not rating else {"destination_id": rating.destination_id, "rating_score": rating.rating_score, "comment": rating.comment}
    return response_success(data, {"request_id": request.state.request_id})


def _rec_item(s: dict) -> dict:
    d = destination_to_dict(s["destination"], categories=None)
    d["categories"] = s["categories"]
    return {
        "destination": d,
        "match": s["match"],
        "reasons": s["reasons"],
        "components": s["components"],
    }


def _profile_out(p: dict) -> dict:
    return {
        "top_categories": p["top_categories"],
        "preferred_price": p["preferred_price"],
        "is_new": p["is_new"],
    }


@router.get("/recommendations")
def recommendations(
    request: Request,
    limit: int = Query(default=10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.recommendation import RecommendationService

    service = RecommendationService(db)
    rec = service.recommendations(current_user.id, limit)
    return response_success(
        {
            "matched": [_rec_item(s) for s in rec["matched"]],
            "explore": [_rec_item(s) for s in rec["explore"]],
            "profile": _profile_out(rec["profile"]),
        },
        {"request_id": request.state.request_id},
    )


@router.get("/itinerary")
def itinerary(
    request: Request,
    limit: int = Query(default=5, ge=1, le=10),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from app.services.recommendation import RecommendationService

    service = RecommendationService(db)
    plan = service.itinerary(current_user.id, limit)
    items = []
    for it in plan["itinerary"]:
        cats = service.repo.categories_for(it["destination"].id)
        d = destination_to_dict(it["destination"], categories=cats)
        items.append({
            "order": it["order"],
            "destination": d,
            "match": it["match"],
            "reasons": it["reasons"],
            "slot": it["slot"],
        })
    return response_success(
        {"itinerary": items, "total_match": plan["total_match"], "profile": _profile_out(plan["profile"])},
        {"request_id": request.state.request_id},
    )
