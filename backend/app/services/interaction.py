from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.models import Destination, Favorite, Rating


class InteractionService:
    def __init__(self, db: Session):
        self.db = db

    def _active_destination(self, destination_id: int) -> Destination:
        dest = self.db.get(Destination, destination_id)
        if not dest or dest.status != "active":
            raise AppError("NOT_FOUND", "Destination not found", 404)
        return dest

    def favorite(self, user_id: int, destination_id: int) -> Favorite:
        self._active_destination(destination_id)
        fav = self.db.get(Favorite, (user_id, destination_id))
        if fav:
            return fav
        fav = Favorite(user_id=user_id, destination_id=destination_id)
        self.db.add(fav)
        self.db.flush()
        return fav

    def unfavorite(self, user_id: int, destination_id: int) -> None:
        fav = self.db.get(Favorite, (user_id, destination_id))
        if fav:
            self.db.delete(fav)
            self.db.flush()

    def list_favorite_ids(self, user_id: int, offset: int, limit: int) -> list[int]:
        rows = self.db.scalars(
            select(Favorite.destination_id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
            .offset(offset)
            .limit(limit)
        ).all()
        return list(rows)

    def get_rating(self, user_id: int, destination_id: int) -> Rating | None:
        return self.db.get(Rating, (user_id, destination_id))

    def upsert_rating(self, user_id: int, destination_id: int, score: int, comment: str | None) -> Rating:
        self._active_destination(destination_id)
        rating = self.db.get(Rating, (user_id, destination_id))
        if rating:
            rating.rating_score = score
            rating.comment = comment
        else:
            rating = Rating(user_id=user_id, destination_id=destination_id, rating_score=score, comment=comment)
            self.db.add(rating)
        self.db.flush()
        self._recompute_avg(destination_id)
        return rating

    def _recompute_avg(self, destination_id: int) -> None:
        row = self.db.execute(
            select(func.count(Rating.rating_score), func.coalesce(func.avg(Rating.rating_score), 0)).where(
                Rating.destination_id == destination_id
            )
        ).one()
        count, avg = int(row[0] or 0), float(row[1] or 0)
        dest = self.db.get(Destination, destination_id)
        dest.rating_avg = round(avg, 2)
        self.db.flush()
