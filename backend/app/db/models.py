from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    SmallInteger,
    Boolean,
    String,
    Text,
    Numeric,
    ForeignKey,
    TIMESTAMP,
    func,
    JSON,
    CheckConstraint,
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

    tokens = relationship("UserToken", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="actor", cascade="all, delete-orphan")


class UserToken(Base):
    __tablename__ = "user_tokens"

    id = Column(IDType, primary_key=True, autoincrement=True)
    user_id = Column(IDType, ForeignKey("users.id"), nullable=False, index=True)
    token_access = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    revoked_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="tokens")


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
    place_id = Column(String(120), nullable=True, index=True)
    name = Column(String(180), nullable=False)
    slug = Column(String(220), unique=True, nullable=False, index=True)
    address = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    rating_avg = Column(Numeric(3, 2), nullable=False, default=0)
    rating_count = Column(BigInteger, nullable=False, default=0)
    lat = Column(Numeric(10, 7), nullable=True)
    lng = Column(Numeric(10, 7), nullable=True)
    price_level = Column(String(20), nullable=False, default="medium")
    price_raw_text = Column(Text, nullable=True)
    open_hour = Column(String(120), nullable=True)
    open_hours_raw_text = Column(String(200), nullable=True)
    open_hour_open = Column(String(120), nullable=True)
    open_hour_close = Column(String(120), nullable=True)
    img_url = Column(Text, nullable=True)
    img_urls = Column(JSON, nullable=True)
    url_map = Column(Text, nullable=True)
    view_count = Column(BigInteger, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    categories = relationship("CategoryDestination", back_populates="destination", cascade="all, delete-orphan")
    insight = relationship("DestinationInsight", back_populates="destination", uselist=False, cascade="all, delete-orphan")
    metrics = relationship("DestinationMetric", back_populates="destination", uselist=False, cascade="all, delete-orphan")
    activity_mappings = relationship("DestinationActivity", back_populates="destination", cascade="all, delete-orphan")
    features = relationship("DestinationFeature", back_populates="destination", uselist=False, cascade="all, delete-orphan")


class Activity(Base):
    __tablename__ = "activities"

    id = Column(IDType, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    slug = Column(String(160), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    destination_mappings = relationship("DestinationActivity", back_populates="activity", cascade="all, delete-orphan")
    rule = relationship("ActivityRule", back_populates="activity", uselist=False, cascade="all, delete-orphan")


class DestinationActivity(Base):
    __tablename__ = "destination_activities"

    destination_id = Column(IDType, ForeignKey("destinations.id"), primary_key=True)
    activity_id = Column(IDType, ForeignKey("activities.id"), primary_key=True)
    weight = Column(Numeric(4, 3), nullable=False, default=1.0)
    source = Column(String(20), nullable=False, default="manual")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    destination = relationship("Destination", back_populates="activity_mappings")
    activity = relationship("Activity", back_populates="destination_mappings")


class ActivityRule(Base):
    __tablename__ = "activity_rules"

    activity_id = Column(IDType, ForeignKey("activities.id"), primary_key=True)
    scenery_weight = Column(Numeric(5, 4), nullable=False, default=0.25)
    accessibility_weight = Column(Numeric(5, 4), nullable=False, default=0.25)
    crowd_weight = Column(Numeric(5, 4), nullable=False, default=0.25)
    value_weight = Column(Numeric(5, 4), nullable=False, default=0.25)
    crowd_mode = Column(String(20), nullable=False, default="prefer_low")
    min_match_threshold = Column(Numeric(4, 3), nullable=False, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    activity = relationship("Activity", back_populates="rule")


class DestinationFeature(Base):
    __tablename__ = "destination_features"

    destination_id = Column(IDType, ForeignKey("destinations.id"), primary_key=True)
    is_indoor = Column(Boolean, nullable=True)
    is_outdoor = Column(Boolean, nullable=True)
    suitable_time = Column(String(20), nullable=False, default="both")
    budget_level = Column(String(20), nullable=True)
    duration_suggested_minutes = Column(Integer, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    destination = relationship("Destination", back_populates="features")


class CategoryDestination(Base):
    __tablename__ = "category_destinations"

    category_id = Column(IDType, ForeignKey("categories.id"), primary_key=True)
    destination_id = Column(IDType, ForeignKey("destinations.id"), primary_key=True)

    category = relationship("Category", back_populates="destinations")
    destination = relationship("Destination", back_populates="categories")


class DestinationInsight(Base):
    __tablename__ = "destination_insights"

    destination_id = Column(IDType, ForeignKey("destinations.id"), primary_key=True)
    human_override = Column(JSON, nullable=True)
    score_snapshot = Column(JSON, nullable=True)
    final_data = Column(JSON, nullable=False)
    insight_cache = Column(JSON, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    destination = relationship("Destination", back_populates="insight")


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


class DestinationMetric(Base):
    __tablename__ = "destination_metrics"

    destination_id = Column(IDType, ForeignKey("destinations.id"), primary_key=True)
    favorite_count = Column(BigInteger, nullable=False, default=0)
    rating_count = Column(BigInteger, nullable=False, default=0)
    rating_sum = Column(BigInteger, nullable=False, default=0)
    view_count = Column(BigInteger, nullable=False, default=0)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    destination = relationship("Destination", back_populates="metrics")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(IDType, primary_key=True, autoincrement=True)
    actor_user_id = Column(IDType, ForeignKey("users.id"), nullable=True, index=True)
    actor_email = Column(String(255), nullable=True)
    actor_role = Column(String(20), nullable=True)
    action = Column(String(120), nullable=False, index=True)
    target_type = Column(String(80), nullable=True)
    target_id = Column(String(120), nullable=True)
    status = Column(String(20), nullable=False, default="success")
    request_id = Column(String(64), nullable=True, index=True)
    method = Column(String(10), nullable=True)
    path = Column(String(255), nullable=True)
    ip_address = Column(String(64), nullable=True)
    user_agent = Column(Text, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    actor = relationship("User", back_populates="audit_logs")
