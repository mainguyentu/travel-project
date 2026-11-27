from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Alats Travel DaNang API"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/travel"
    redis_url: str = "redis://localhost:6379/0"

    es_url: str = "http://localhost:9200"
    es_enabled: bool = True
    es_index: str = "destinations"

    events_stream: str = "travel-events"
    events_enabled: bool = True

    jwt_secret: str = "dev-only-change-me-please-32chars!!"
    jwt_issuer: str = "alats-travel"
    jwt_access_ttl_min: int = 30
    jwt_refresh_ttl_days: int = 14

    cors_origins: List[str] = [
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ]

    rate_limit_ip_per_min: int = 120
    rate_limit_user_per_min: int = 60

    cache_ttl_seconds: int = 300

    internal_api_key: str = "dev-internal-key"
    activity_recommendation_enabled: bool = True


settings = Settings()
