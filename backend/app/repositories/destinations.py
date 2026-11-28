from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.db.models import (
    Category,
    CategoryDestination,
    Destination,
    DestinationInsight,
    Favorite,
    Rating,
    UserView,
)


class DestinationRepository:
    def __init__(self, db: Session):
        self.db = db

    def _base_query(self, category_slug=None, price_level=None, rating_min=None, keyword=None, status="active", q=None):
        stmt = select(Destination).where(Destination.status == status)
        if category_slug:
            stmt = stmt.join(CategoryDestination, CategoryDestination.destination_id == Destination.id).join(
                Category, Category.id == CategoryDestination.category_id
            ).where(Category.slug == category_slug)
        if price_level:
            stmt = stmt.where(Destination.price_level == price_level)
        if rating_min is not None:
            stmt = stmt.where(Destination.rating_avg >= rating_min)
        text = q if q is not None else keyword
        if text:
            like = f"%{text}%"
            stmt = stmt.where(or_(Destination.name.ilike(like), Destination.address.ilike(like)))
        return stmt

    def list(self, category_slug=None, price_level=None, rating_min=None, keyword=None, sort=None, offset=0, limit=20):
        stmt = self._base_query(category_slug, price_level, rating_min, keyword)
        order = Destination.created_at.desc()
        if sort == "rating":
            order = Destination.rating_avg.desc()
        elif sort == "views":
            order = Destination.view_count.desc()
        elif sort == "name":
            order = Destination.name.asc()
        return list(self.db.scalars(stmt.order_by(order).offset(offset).limit(limit)).all())

    def count(self, category_slug=None, price_level=None, rating_min=None, keyword=None) -> int:
        stmt = select(func.count()).select_from(self._base_query(category_slug, price_level, rating_min, keyword).subquery())
        return int(self.db.scalar(stmt) or 0)

    def search(self, q="", category_slug=None, price_level=None, offset=0, limit=20):
        return self.list(category_slug, price_level, None, q or None, None, offset, limit)

    def get_by_ids(self, ids: list):
        if not ids:
            return []
        return list(self.db.scalars(select(Destination).where(Destination.id.in_(ids))).all())

    def get_detail(self, destination_id: int) -> Destination | None:
        return self.db.get(Destination, destination_id)

    def increment_view(self, destination_id: int) -> None:
        self.db.query(Destination).filter_by(id=destination_id).update(
            {Destination.view_count: Destination.view_count + 1}
        )

    def record_user_view(self, user_id: int | None, destination_id: int) -> None:
        """Ghi thói quen xem per-user (fire-and-forget từ detail)."""
        if not user_id:
            return
        from datetime import datetime, timezone

        row = self.db.get(UserView, (user_id, destination_id))
        if row:
            row.view_count = int(row.view_count or 0) + 1
            row.last_viewed_at = datetime.now(timezone.utc)
        else:
            self.db.add(UserView(user_id=user_id, destination_id=destination_id, view_count=1))

    def user_profile_signals(self, user_id: int) -> dict:
        """Tín hiệu thô cho recommendation: favorites + views per-user (kèm categories)."""
        fav_ids = list(
            self.db.scalars(select(Favorite.destination_id).where(Favorite.user_id == user_id)).all()
        )
        view_rows = list(
            self.db.scalars(select(UserView).where(UserView.user_id == user_id)).all()
        )
        return {"favorite_ids": fav_ids, "views": {r.destination_id: int(r.view_count or 1) for r in view_rows}}

    def top_favorites(self, limit=6, from_date=None, to_date=None) -> list:
        join_cond = Favorite.destination_id == Destination.id
        if from_date:
            join_cond = join_cond & (Favorite.created_at >= from_date)
        if to_date:
            join_cond = join_cond & (Favorite.created_at <= to_date)
        stmt = (
            select(Destination, func.count(Favorite.destination_id).label("cnt"))
            .outerjoin(Favorite, join_cond)
            .where(Destination.status == "active")
            .group_by(Destination.id)
            .order_by(func.count(Favorite.destination_id).desc(), Destination.rating_avg.desc())
            .limit(limit)
        )
        return [row[0] for row in self.db.execute(stmt).all()]

    def top_ratings(self, limit=6, from_date=None, to_date=None) -> list:
        if from_date or to_date:
            join_cond = Rating.destination_id == Destination.id
            if from_date:
                join_cond = join_cond & (Rating.created_at >= from_date)
            if to_date:
                join_cond = join_cond & (Rating.created_at <= to_date)
            stmt = (
                select(Destination, func.coalesce(func.avg(Rating.rating_score), 0).label("avg"))
                .outerjoin(Rating, join_cond)
                .where(Destination.status == "active")
                .group_by(Destination.id)
                .order_by(func.coalesce(func.avg(Rating.rating_score), 0).desc(), Destination.view_count.desc())
                .limit(limit)
            )
            return [row[0] for row in self.db.execute(stmt).all()]
        return list(
            self.db.scalars(
                select(Destination)
                .where(Destination.status == "active")
                .order_by(Destination.rating_avg.desc(), Destination.view_count.desc())
                .limit(limit)
            ).all()
        )

    def top_views(self, limit=6) -> list:
        return list(
            self.db.scalars(
                select(Destination)
                .where(Destination.status == "active")
                .order_by(Destination.view_count.desc())
                .limit(limit)
            ).all()
        )

    def categories_with_counts(self) -> list:
        rows = self.db.execute(
            select(Category, func.count(CategoryDestination.destination_id).label("cnt"))
            .outerjoin(CategoryDestination, CategoryDestination.category_id == Category.id)
            .group_by(Category.id)
            .order_by(Category.name.asc())
        ).all()
        return [{"category": c, "count": cnt} for c, cnt in rows]

    def insight_for(self, destination_id: int) -> DestinationInsight | None:
        return self.db.get(DestinationInsight, destination_id)

    def favorite_count(self, destination_id: int) -> int:
        return int(
            self.db.scalar(
                select(func.count()).select_from(Favorite).where(Favorite.destination_id == destination_id)
            ) or 0
        )

    def rating_stats(self, destination_id: int) -> tuple[int, int]:
        row = self.db.execute(
            select(func.count(Rating.destination_id), func.coalesce(func.sum(Rating.rating_score), 0)).where(
                Rating.destination_id == destination_id
            )
        ).one()
        return int(row[0] or 0), int(row[1] or 0)

    def categories_for(self, destination_id: int) -> list:
        return list(
            self.db.scalars(
                select(Category)
                .join(CategoryDestination, CategoryDestination.category_id == Category.id)
                .where(CategoryDestination.destination_id == destination_id)
                .order_by(Category.name.asc())
            ).all()
        )
