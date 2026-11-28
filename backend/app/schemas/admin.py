from pydantic import BaseModel, Field


class UserStatusUpdate(BaseModel):
    status: str = Field(pattern="^(active|locked)$")


class UserRoleUpdate(BaseModel):
    role: str = Field(pattern="^(user|admin)$")


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    slug: str = Field(min_length=1, max_length=160)
    descriptions: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    slug: str | None = Field(default=None, min_length=1, max_length=160)
    descriptions: str | None = None


class DestinationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    slug: str = Field(min_length=1, max_length=220)
    address: str | None = None
    description: str | None = None
    price_level: str = Field(default="medium", pattern="^(free|low|medium|high)$")
    open_hour: str | None = Field(default=None, max_length=120)
    img_url: str | None = None
    url_map: str | None = None
    lat: float | None = None
    lng: float | None = None
    status: str = Field(default="active", pattern="^(active|inactive)$")
    category_slugs: list[str] = Field(default_factory=list)
    external_rating_avg: float | None = Field(default=None, ge=0, le=5)
    external_rating_count: int | None = Field(default=None, ge=0)
    external_source: str | None = Field(default=None, max_length=80)


class DestinationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    slug: str | None = Field(default=None, min_length=1, max_length=220)
    address: str | None = None
    description: str | None = None
    price_level: str | None = Field(default=None, pattern="^(free|low|medium|high)$")
    open_hour: str | None = Field(default=None, max_length=120)
    img_url: str | None = None
    url_map: str | None = None
    lat: float | None = None
    lng: float | None = None
    status: str | None = Field(default=None, pattern="^(active|inactive)$")
    category_slugs: list[str] | None = None
    external_rating_avg: float | None = Field(default=None, ge=0, le=5)
    external_rating_count: int | None = Field(default=None, ge=0)
    external_source: str | None = Field(default=None, max_length=80)


class DestinationBulkCreate(BaseModel):
    items: list[DestinationCreate] = Field(min_length=1, max_length=100)
