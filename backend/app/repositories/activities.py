from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import (
    Activity,
    ActivityRule,
    Destination,
    DestinationActivity,
    DestinationFeature,
    DestinationInsight,
)


class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_slug(self, slug: str, *, active_only: bool = True) -> Activity | None:
        stmt = select(Activity).where(Activity.slug == slug)
        if active_only:
            stmt = stmt.where(Activity.is_active.is_(True))
        return self.db.execute(stmt).scalar_one_or_none()

    def list_active(self) -> list[Activity]:
        stmt = select(Activity).where(Activity.is_active.is_(True)).order_by(Activity.name.asc())
        return self.db.execute(stmt).scalars().all()

    def get_rule(self, activity_id: int) -> ActivityRule | None:
        stmt = select(ActivityRule).where(ActivityRule.activity_id == activity_id)
        return self.db.execute(stmt).scalar_one_or_none()


class DestinationActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_mapping(self, activity_id: int, destination_id: int) -> DestinationActivity | None:
        stmt = select(DestinationActivity).where(
            DestinationActivity.activity_id == activity_id,
            DestinationActivity.destination_id == destination_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def count_candidates(self, activity_id: int) -> int:
        stmt = (
            select(func.count(DestinationActivity.destination_id))
            .join(Destination, Destination.id == DestinationActivity.destination_id)
            .where(DestinationActivity.activity_id == activity_id, Destination.status == "active")
        )
        return int(self.db.execute(stmt).scalar_one() or 0)

    def list_candidates(
        self,
        activity_id: int,
        *,
        offset: int,
        limit: int,
    ) -> list[tuple[DestinationActivity, Destination, DestinationInsight | None, DestinationFeature | None]]:
        stmt = (
            select(DestinationActivity, Destination, DestinationInsight, DestinationFeature)
            .join(Destination, Destination.id == DestinationActivity.destination_id)
            .outerjoin(DestinationInsight, DestinationInsight.destination_id == Destination.id)
            .outerjoin(DestinationFeature, DestinationFeature.destination_id == Destination.id)
            .where(DestinationActivity.activity_id == activity_id, Destination.status == "active")
            .order_by(DestinationActivity.weight.desc(), Destination.id.asc())
            .offset(offset)
            .limit(limit)
        )
        return self.db.execute(stmt).all()
