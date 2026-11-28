from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    TIMESTAMP,
    CheckConstraint,
    func,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db.base import Base

IDType = BigInteger().with_variant(Integer, "sqlite")


class User(Base):
    __tablename__ = "users"

    id = Column(IDType, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), nullable=False, default="user")
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(IDType, primary_key=True, autoincrement=True)
    user_id = Column(IDType, ForeignKey("users.id"), nullable=False, index=True)
    token_access = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    revoked_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class Category(Base):
    __tablename__ = "categories"

    id = Column(IDType, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    slug = Column(String(160), unique=True, nullable=False, index=True)
    descriptions = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    destinations = relationship("CategoryDestination", back_populates="category", cascade="all, delete-orphan")


class Destination(Base):
    __tablename__ = "destinations"

    id = Column(IDType, primary_key=True, autoincrement=True)
    name = Column(String(180), nullable=False)
    slug = Column(String(220), unique=True, nullable=False, index=True)
    address = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    rating_avg = Column(Numeric(3, 2), nullable=False, default=0)
    lat = Column(Numeric(10, 7), nullable=True)
    lng = Column(Numeric(10, 7), nullable=True)
    price_level = Column(String(20), nullable=False, default="medium")
    open_hour = Column(String(120), nullable=True)
    img_url = Column(Text, nullable=True)
    url_map = Column(Text, nullable=True)
    view_count = Column(BigInteger, nullable=False, default=0)
    external_rating_avg = Column(Numeric(3, 2), nullable=False, default=0)
    external_rating_count = Column(BigInteger, nullable=False, default=0)
    external_source = Column(String(80), nullable=False, default="manual")
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    categories = relationship("CategoryDestination", back_populates="destination", cascade="all, delete-orphan")
    insight = relationship("DestinationInsight", back_populates="destination", uselist=False, cascade="all, delete-orphan")


class CategoryDestination(Base):
    __tablename__ = "category_destinations"

    category_id = Column(IDType, ForeignKey("categories.id"), primary_key=True)
    destination_id = Column(IDType, ForeignKey("destinations.id"), primary_key=True)

    category = relationship("Category", back_populates="destinations")
    destination = relationship("Destination", back_populates="categories")


class DestinationInsight(Base):
    __tablename__ = "destination_insights"

    destination_id = Column(IDType, ForeignKey("destinations.id"), primary_key=True)
    final_data = Column(JSON, nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    destination = relationship("Destination", back_populates="insight")


class UserView(Base):
    __tablename__ = "user_views"

    user_id = Column(IDType, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    destination_id = Column(IDType, ForeignKey("destinations.id", ondelete="CASCADE"), primary_key=True)
    view_count = Column(Integer, nullable=False, default=1)
    last_viewed_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)


class Favorite(Base):
    __tablename__ = "favorites"

    user_id = Column(IDType, ForeignKey("users.id"), primary_key=True)
    destination_id = Column(IDType, ForeignKey("destinations.id"), primary_key=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    deleted_at = Column(TIMESTAMP(timezone=True), nullable=True)


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (CheckConstraint("rating_score BETWEEN 1 AND 5", name="ck_ratings_score"),)

    user_id = Column(IDType, ForeignKey("users.id"), primary_key=True)
    destination_id = Column(IDType, ForeignKey("destinations.id"), primary_key=True)
    rating_score = Column(SmallInteger, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(IDType, primary_key=True, autoincrement=True)
    actor_user_id = Column(IDType, ForeignKey("users.id"), nullable=True, index=True)
    action = Column(String(80), nullable=False)
    entity = Column(String(80), nullable=False)
    entity_id = Column(String(80), nullable=True)
    detail = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
