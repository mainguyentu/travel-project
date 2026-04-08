from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.repositories.interaction import InteractionRepository
from app.repositories.destinations import DestinationRepository
from app.core.cache import invalidate_admin_stats_cache, invalidate_destination_cache, invalidate_public_landing_cache
from app.services.insight import InsightService


class InteractionService:
    def __init__(self, db: Session):
        self.db = db
        self.interactions = InteractionRepository(db)
        self.destinations = DestinationRepository(db)

    def favorite(self, user_id: int, destination_id: int):
        destination = self.destinations.get_by_id(destination_id)
        if not destination or destination.status != "active":
            raise AppError("NOT_FOUND", "Destination not found", status_code=404)
        fav = self.interactions.upsert_favorite(user_id, destination_id)
        invalidate_admin_stats_cache()
        invalidate_public_landing_cache()
        return fav

    def unfavorite(self, user_id: int, destination_id: int):
        self.interactions.soft_delete_favorite(user_id, destination_id)
        invalidate_admin_stats_cache()
        invalidate_public_landing_cache()

    def upsert_rating(self, user_id: int, destination_id: int, rating_score: int, comment: str | None):
        destination = self.destinations.get_by_id(destination_id)
        if not destination or destination.status != "active":
            raise AppError("NOT_FOUND", "Destination not found", status_code=404)
        old_rating = self.interactions.get_rating(user_id, destination_id)
        old_score = old_rating.rating_score if old_rating else None
        old_comment = old_rating.comment if old_rating else None

        rating = self.interactions.upsert_rating(user_id, destination_id, rating_score, comment)
        InsightService(self.db).apply_rating_update(
            destination_id=destination_id,
            new_score=rating_score,
            new_comment=comment,
            old_score=old_score,
            old_comment=old_comment,
            is_new_rating=old_rating is None,
        )
        self.destinations.recompute_rating_avg(destination_id)
        invalidate_destination_cache(destination_id)
        invalidate_admin_stats_cache()
        invalidate_public_landing_cache()
        return rating

    def get_rating(self, user_id: int, destination_id: int):
        return self.interactions.get_rating(user_id, destination_id)
