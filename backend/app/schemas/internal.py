from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class IdsRequest(BaseModel):
    ids: list[int] = Field(default_factory=list)


class ApplyRatingInsightRequest(BaseModel):
    new_score: int
    new_comment: str | None = None

    old_score: int | None = None
    old_comment: str | None = None

    new_review_time: datetime | str | None = None
    old_review_time: datetime | str | None = None

    is_new_rating: bool = False
    reviewer_user_id: int | None = None

