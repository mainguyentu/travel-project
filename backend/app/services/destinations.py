from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.errors import AppError
from app.db.models import Category
from app.repositories.destinations import DestinationRepository
from app.repositories.categories import CategoryRepository
from app.core.cache import invalidate_destination_cache, invalidate_admin_stats_cache, invalidate_public_landing_cache


class DestinationService:
    def __init__(self, db: Session):
        self.db = db
        self.destinations = DestinationRepository(db)
        self.categories = CategoryRepository(db)

    def _validate_categories(self, category_ids: list[int]):
        if not category_ids:
            return
        stmt = select(Category.id).where(Category.id.in_(category_ids))
        rows = self.db.execute(stmt).scalars().all()
        if len(rows) != len(set(category_ids)):
            raise AppError("VALIDATION_ERROR", "Invalid category_ids", status_code=400)

    def create(self, data: dict, category_ids: list[int]):
        self._validate_categories(category_ids)
        destination = self.destinations.create(data)
        if category_ids:
            self.destinations.set_categories(destination, category_ids)
        invalidate_destination_cache(destination.id)
        invalidate_admin_stats_cache()
        invalidate_public_landing_cache()
        return destination

    def update(self, destination_id: int, data: dict, category_ids: list[int] | None):
        destination = self.destinations.get_by_id(destination_id)
        if not destination:
            raise AppError("NOT_FOUND", "Destination not found", status_code=404)
        destination = self.destinations.update(destination, data)
        if category_ids is not None:
            self._validate_categories(category_ids)
            self.destinations.set_categories(destination, category_ids)
        invalidate_destination_cache(destination_id)
        invalidate_admin_stats_cache()
        invalidate_public_landing_cache()
        return destination

    def delete(self, destination_id: int):
        destination = self.destinations.get_by_id(destination_id)
        if not destination:
            raise AppError("NOT_FOUND", "Destination not found", status_code=404)
        self.destinations.delete(destination)
        invalidate_destination_cache(destination_id)
        invalidate_admin_stats_cache()
        invalidate_public_landing_cache()

    def get_detail(self, destination_id: int, increment_view: bool = True):
        destination = self.destinations.get_by_id(destination_id)
        if not destination or destination.status != "active":
            raise AppError("NOT_FOUND", "Destination not found", status_code=404)
        if increment_view:
            destination.view_count += 1
            self.db.flush()
        return destination
