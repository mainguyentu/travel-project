from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, update
from app.db.models import Destination, Category, CategoryDestination, Rating, Favorite


class DestinationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, destination_id: int) -> Destination | None:
        return self.db.get(Destination, destination_id)

    def get_by_slug(self, slug: str) -> Destination | None:
        stmt = select(Destination).where(Destination.slug == slug)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(
        self,
        category_slug: str | None,
        price_level: str | None,
        rating_min: float | None,
        keyword: str | None,
        sort: str | None,
        offset: int,
        limit: int,
    ):
        stmt = select(Destination).where(Destination.status == "active")
        if category_slug:
            stmt = stmt.join(CategoryDestination).join(Category).where(Category.slug == category_slug)
        if price_level:
            stmt = stmt.where(Destination.price_level == price_level)
        if rating_min is not None:
            stmt = stmt.where(Destination.rating_avg >= rating_min)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(Destination.name.ilike(like), Destination.description.ilike(like)))
        if sort == "rating":
            stmt = stmt.order_by(Destination.rating_avg.desc())
        elif sort == "views":
            stmt = stmt.order_by(Destination.view_count.desc())
        else:
            stmt = stmt.order_by(Destination.created_at.desc())
        stmt = stmt.offset(offset).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def count(self, category_slug: str | None, price_level: str | None, rating_min: float | None, keyword: str | None):
        stmt = select(func.count(Destination.id)).where(Destination.status == "active")
        if category_slug:
            stmt = stmt.join(CategoryDestination).join(Category).where(Category.slug == category_slug)
        if price_level:
            stmt = stmt.where(Destination.price_level == price_level)
        if rating_min is not None:
            stmt = stmt.where(Destination.rating_avg >= rating_min)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(Destination.name.ilike(like), Destination.description.ilike(like)))
        return self.db.execute(stmt).scalar_one()

    def list_admin(self, status: str | None, offset: int, limit: int):
        stmt = select(Destination)
        if status:
            stmt = stmt.where(Destination.status == status)
        stmt = stmt.order_by(Destination.created_at.desc()).offset(offset).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def count_admin(self, status: str | None):
        stmt = select(func.count(Destination.id))
        if status:
            stmt = stmt.where(Destination.status == status)
        return self.db.execute(stmt).scalar_one()

    def search(self, q: str, category_slug: str | None, price_level: str | None, offset: int, limit: int):
        stmt = select(Destination).where(Destination.status == "active")
        if q:
            like = f"%{q}%"
            stmt = stmt.where(or_(Destination.name.ilike(like), Destination.description.ilike(like)))
        if category_slug:
            stmt = stmt.join(CategoryDestination).join(Category).where(Category.slug == category_slug)
        if price_level:
            stmt = stmt.where(Destination.price_level == price_level)
        stmt = stmt.order_by(Destination.rating_avg.desc()).offset(offset).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def create(self, data: dict) -> Destination:
        destination = Destination(**data)
        self.db.add(destination)
        self.db.flush()
        return destination

    def update(self, destination: Destination, data: dict) -> Destination:
        for k, v in data.items():
            setattr(destination, k, v)
        self.db.flush()
        return destination

    def delete(self, destination: Destination) -> None:
        self.db.delete(destination)
        self.db.flush()

    def set_categories(self, destination: Destination, category_ids: list[int]):
        destination.categories.clear()
        for category_id in category_ids:
            destination.categories.append(CategoryDestination(category_id=category_id, destination_id=destination.id))
        self.db.flush()

    def top_by_rating(self, limit: int = 5):
        stmt = select(Destination).where(Destination.status == "active").order_by(Destination.rating_avg.desc()).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def top_by_views(self, limit: int = 5):
        stmt = select(Destination).where(Destination.status == "active").order_by(Destination.view_count.desc()).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def top_by_favorites(self, limit: int = 5):
        subq = (
            select(Favorite.destination_id, func.count(Favorite.destination_id).label("cnt"))
            .where(Favorite.deleted_at.is_(None))
            .group_by(Favorite.destination_id)
            .subquery()
        )
        stmt = (
            select(Destination)
            .join(subq, subq.c.destination_id == Destination.id)
            .where(Destination.status == "active")
            .order_by(subq.c.cnt.desc())
            .limit(limit)
        )
        return self.db.execute(stmt).scalars().all()

    def recompute_rating_avg(self, destination_id: int):
        stmt = select(func.avg(Rating.rating_score)).where(Rating.destination_id == destination_id)
        avg = self.db.execute(stmt).scalar_one() or 0
        destination = self.get_by_id(destination_id)
        if destination:
            destination.rating_avg = round(float(avg), 2)
            self.db.flush()

    def increment_view(self, destination_id: int) -> None:
        stmt = update(Destination).where(Destination.id == destination_id).values(view_count=Destination.view_count + 1)
        self.db.execute(stmt)
