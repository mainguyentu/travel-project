from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models import Favorite, Rating, Destination


class InteractionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_favorite(self, user_id: int, destination_id: int) -> Favorite | None:
        stmt = select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.destination_id == destination_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def upsert_favorite(self, user_id: int, destination_id: int) -> Favorite:
        fav = self.get_favorite(user_id, destination_id)
        if fav:
            fav.deleted_at = None
            self.db.flush()
            return fav
        fav = Favorite(user_id=user_id, destination_id=destination_id)
        self.db.add(fav)
        self.db.flush()
        return fav

    def soft_delete_favorite(self, user_id: int, destination_id: int) -> None:
        fav = self.get_favorite(user_id, destination_id)
        if fav and fav.deleted_at is None:
            fav.deleted_at = datetime.now(timezone.utc)
            self.db.flush()

    def list_favorites(self, user_id: int, offset: int, limit: int):
        stmt = (
            select(Destination)
            .join(Favorite, Favorite.destination_id == Destination.id)
            .where(Favorite.user_id == user_id, Favorite.deleted_at.is_(None))
            .offset(offset)
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def get_rating(self, user_id: int, destination_id: int) -> Rating | None:
        stmt = select(Rating).where(Rating.user_id == user_id, Rating.destination_id == destination_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def upsert_rating(self, user_id: int, destination_id: int, rating_score: int, comment: str | None) -> Rating:
        rating = self.get_rating(user_id, destination_id)
        if rating:
            rating.rating_score = rating_score
            rating.comment = comment
            self.db.flush()
            return rating
        rating = Rating(user_id=user_id, destination_id=destination_id, rating_score=rating_score, comment=comment)
        self.db.add(rating)
        self.db.flush()
        return rating
