import json
import logging
from typing import Any
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

_redis_client = None


def get_redis():
    global _redis_client
    if not settings.redis_url:
        return None
    if _redis_client is None:
        try:
            _redis_client = redis.Redis.from_url(
                settings.redis_url,
                decode_responses=True,
                max_connections=settings.redis_max_connections,
                socket_connect_timeout=settings.redis_socket_connect_timeout,
                socket_timeout=settings.redis_socket_timeout,
            )
        except Exception as exc:
            logger.warning("Redis init failed: %s", exc)
            _redis_client = None
    return _redis_client


def cache_get(key: str) -> Any | None:
    r = get_redis()
    if not r:
        return None
    try:
        val = r.get(key)
        if val is None:
            return None
        return json.loads(val)
    except Exception as exc:
        logger.warning("Redis get failed: %s", exc)
        return None


def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    r = get_redis()
    if not r:
        return
    try:
        payload = json.dumps(value, ensure_ascii=False)
        r.setex(key, ttl or settings.cache_ttl_seconds, payload)
    except Exception as exc:
        logger.warning("Redis set failed: %s", exc)


def cache_delete(key: str) -> None:
    r = get_redis()
    if not r:
        return
    try:
        r.delete(key)
    except Exception as exc:
        logger.warning("Redis delete failed: %s", exc)


def cache_delete_pattern(pattern: str) -> None:
    r = get_redis()
    if not r:
        return
    try:
        cursor = 0
        while True:
            cursor, keys = r.scan(cursor=cursor, match=pattern, count=200)
            if keys:
                r.delete(*keys)
            if cursor == 0:
                break
    except Exception as exc:
        logger.warning("Redis scan delete failed: %s", exc)


def key_dest_list(category: str | None, price: str | None, rating: float | None, page: int, sort: str | None, keyword: str | None) -> str:
    return f"destinations:list:{category or 'all'}:{price or 'all'}:{rating if rating is not None else 'all'}:{page}:{sort or 'default'}:{keyword or 'all'}"


def key_dest_detail(destination_id: int) -> str:
    return f"destination:detail:{destination_id}"


def key_admin_top(kind: str) -> str:
    return f"admin:top:{kind}"


def invalidate_destination_cache(destination_id: int) -> None:
    cache_delete(key_dest_detail(destination_id))
    cache_delete_pattern("destinations:list:*")


def invalidate_list_cache() -> None:
    cache_delete_pattern("destinations:list:*")


def invalidate_admin_stats_cache() -> None:
    cache_delete_pattern("admin:top:*")


def invalidate_public_landing_cache() -> None:
    cache_delete("public:landing")
