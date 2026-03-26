from pydantic import BaseModel, Field


class RatingUpsert(BaseModel):
    rating_score: int = Field(ge=1, le=5)
    comment: str | None = None


class RatingOut(BaseModel):
    destination_id: int
    rating_score: int
    comment: str | None


class FavoriteOut(BaseModel):
    destination_id: int
