from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Alats Travel DaNang API"
    api_prefix: str = "/api/v1"
    log_level: str = "INFO"

    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/travel"

    jwt_secret: str = "change-me"
    jwt_issuer: str = "alats-travel"
    jwt_access_ttl_min: int = 30
    jwt_refresh_ttl_days: int = 14

    cors_origins: List[str] = ["*"]

    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 300
    rate_limit_ip_per_min: int = 120
    rate_limit_user_per_min: int = 60


settings = Settings()
