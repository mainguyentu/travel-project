from pydantic import BaseModel, Field
from typing import List


class DestinationBase(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    slug: str = Field(min_length=1, max_length=220)
    address: str | None = None
    description: str | None = None
    price_level: str = "medium"
    open_hour: str | None = None
    img_url: str | None = None
    url_map: str | None = None
    lat: float | None = None
    lng: float | None = None
    status: str = "active"


class DestinationCreate(DestinationBase):
    category_ids: List[int] = []


class DestinationUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=180)
    slug: str | None = Field(default=None, max_length=220)
    address: str | None = None
    description: str | None = None
    price_level: str | None = None
    open_hour: str | None = None
    img_url: str | None = None
    url_map: str | None = None
    lat: float | None = None
    lng: float | None = None
    status: str | None = None
    category_ids: List[int] | None = None


class DestinationOut(BaseModel):
    id: int
    name: str
    slug: str
    address: str | None
    description: str | None
    rating_avg: float
    lat: float | None
    lng: float | None
    price_level: str
    open_hour: str | None
    img_url: str | None
    url_map: str | None
    view_count: int
    status: str
    categories: List[dict] = []


class LandingOut(BaseModel):
    highlights: List[DestinationOut]
    categories: List[dict]
    top_ratings: List[DestinationOut]
    top_favorites: List[DestinationOut]
