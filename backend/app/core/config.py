from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import json


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Alats Travel DaNang API"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/travel"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    jwt_secret: str = "dev-only-change-me-please-32chars!!"
    jwt_issuer: str = "alats-travel"
    jwt_access_ttl_min: int = 30
    jwt_refresh_ttl_days: int = 14

    cors_origins: List[str] = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
    ]

    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 100
    redis_socket_connect_timeout: float = 2.0
    redis_socket_timeout: float = 2.0
    cache_ttl_seconds: int = 300
    rate_limit_ip_per_min: int = 120
    rate_limit_user_per_min: int = 60

    kafka_enabled: bool = False
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_client_id: str = "travel-backend"
    kafka_topic_favorite: str = "favorite-events"
    kafka_topic_rating: str = "rating-events"
    kafka_topic_destination: str = "destination-events"
    kafka_topic_view: str = "view-events"
    kafka_dlq_topic: str = "travel-events-dlq"
    kafka_consumer_group: str = "travel-worker-group"

    elasticsearch_enabled: bool = False
    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "travel_destinations"
    search_use_elasticsearch: bool = False

    worker_retry_max: int = 3
    worker_retry_backoff_seconds: float = 0.5

    @field_validator("jwt_secret")
    @classmethod
    def validate_jwt_secret(cls, value: str) -> str:
        if len(value) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            text = value.strip()
            if text.startswith("["):
                return json.loads(text)
            return [item.strip() for item in text.split(",") if item.strip()]
        return value

    @field_validator("cors_origins")
    @classmethod
    def validate_cors_origins(cls, value: List[str]) -> List[str]:
        if not value:
            raise ValueError("CORS_ORIGINS cannot be empty")
        if "*" in value:
            raise ValueError("Wildcard CORS origin '*' is not allowed; use an explicit whitelist")
        return value

    @field_validator("db_pool_size", "db_max_overflow", "db_pool_timeout", "db_pool_recycle", "redis_max_connections")
    @classmethod
    def validate_positive_int(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("pool settings must be > 0")
        return value

    @field_validator("worker_retry_max")
    @classmethod
    def validate_worker_retry_max(cls, value: int) -> int:
        if value < 0:
            raise ValueError("worker_retry_max must be >= 0")
        return value

    @field_validator("redis_socket_connect_timeout", "redis_socket_timeout")
    @classmethod
    def validate_positive_float(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("redis socket timeouts must be > 0")
        return value

    @field_validator("worker_retry_backoff_seconds")
    @classmethod
    def validate_retry_backoff(cls, value: float) -> float:
        if value < 0:
            raise ValueError("worker_retry_backoff_seconds must be >= 0")
        return value


settings = Settings()
