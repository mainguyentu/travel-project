from pydantic import BaseModel, Field
from typing import List


class DestinationPriceInput(BaseModel):
    raw_text: str | None = None
    level: str | None = None


class DestinationOpenHoursInput(BaseModel):
    raw_text: str | None = None
    open: str | None = None
    close: str | None = None


class DestinationReviewInput(BaseModel):
    author: str | None = None
    rating: float | int | None = None
    when: str | None = None
    text: str | None = None


class DestinationBase(BaseModel):
    place_id: str | None = None
    name: str = Field(min_length=1, max_length=180)
    slug: str | None = Field(default=None, min_length=1, max_length=220)
    address: str | None = None
    description: str | None = None
    rating: float | None = None
    rating_avg: float = 0
    rating_count: int = 0
    price_level: str = "medium"
    price_raw_text: str | None = None
    price: DestinationPriceInput | str | None = None
    open_hour: str | None = None
    open_hours_raw_text: str | None = None
    open_hour_open: str | None = None
    open_hour_close: str | None = None
    open_hours: DestinationOpenHoursInput | None = None
    img_url: str | List[str] | None = None
    img_urls: List[str] | None = None
    image: List[str] | None = None
    url_map: str | None = None
    maps_url: str | None = None
    category: List[str] | None = None
    reviews: List[DestinationReviewInput] | None = None
    lat: float | None = None
    lng: float | None = None
    view_count: int = 0
    status: str = "active"


class DestinationCreate(DestinationBase):
    category_ids: List[int] = []


class DestinationBulkCreate(BaseModel):
    destinations: List[DestinationCreate] = Field(min_length=1, max_length=100)


class DestinationUpdate(BaseModel):
    place_id: str | None = None
    name: str | None = Field(default=None, max_length=180)
    slug: str | None = Field(default=None, max_length=220)
    address: str | None = None
    description: str | None = None
    rating: float | None = None
    rating_avg: float | None = None
    rating_count: int | None = None
    price_level: str | None = None
    price_raw_text: str | None = None
    price: DestinationPriceInput | None = None
    open_hour: str | None = None
    open_hours_raw_text: str | None = None
    open_hour_open: str | None = None
    open_hour_close: str | None = None
    open_hours: DestinationOpenHoursInput | None = None
    img_url: str | List[str] | None = None
    img_urls: List[str] | None = None
    url_map: str | None = None
    lat: float | None = None
    lng: float | None = None
    view_count: int | None = None
    status: str | None = None
    category_ids: List[int] | None = None


class DestinationOut(BaseModel):
    id: int
    place_id: str | None
    name: str
    slug: str
    address: str | None
    description: str | None
    rating_avg: float
    rating_count: int
    lat: float | None
    lng: float | None
    price_level: str
    price_raw_text: str | None
    price: dict | None
    open_hour: str | None
    open_hours_raw_text: str | None
    open_hour_open: str | None
    open_hour_close: str | None
    open_hours: dict | None
    img_url: str | None
    img_urls: List[str] | None
    url_map: str | None
    view_count: int
    status: str
    categories: List[dict] = []


class LandingOut(BaseModel):
    highlights: List[DestinationOut]
    categories: List[dict]
    top_ratings: List[DestinationOut]
    top_favorites: List[DestinationOut]
