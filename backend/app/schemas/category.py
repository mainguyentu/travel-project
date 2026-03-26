from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=160)
    descriptions: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    slug: str | None = Field(default=None, max_length=160)
    descriptions: str | None = None


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    descriptions: str | None
