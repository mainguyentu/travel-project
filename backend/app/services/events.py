import json
import logging
import time

from app.core.config import settings

log = logging.getLogger(__name__)

_redis = None


def get_redis():
    global _redis
    if _redis is not None:
        return _redis
    try:
        import redis as redis_lib

        r = redis_lib.Redis.from_url(settings.redis_url, socket_connect_timeout=3)
        r.ping()
        _redis = r
        return r
    except Exception as exc:
        log.warning("redis unavailable (%s); events disabled", exc)
        return None


def publish(event_type: str, payload: dict) -> bool:
    if not settings.events_enabled:
        return False
    r = get_redis()
    if r is None:
        return False
    try:
        r.xadd(settings.events_stream, {"type": event_type, "data": json.dumps(payload)}, maxlen=10000)
        return True
    except Exception as exc:
        log.warning("publish %s failed: %s", event_type, exc)
        return False


def read_new(last_id: str = "$", count: int = 50, block_ms: int = 2000):
    r = get_redis()
    if r is None:
        return [], last_id
    try:
        res = r.xread({settings.events_stream: last_id}, count=count, block=block_ms)
        if not res:
            return [], last_id
        entries = res[0][1]
        out = []
        for entry_id, fields in entries:
            eid = entry_id.decode() if isinstance(entry_id, bytes) else str(entry_id)
            item = {}
            for k, v in fields.items():
                ks = k.decode() if isinstance(k, bytes) else str(k)
                vs = v.decode() if isinstance(v, bytes) else str(v)
                item[ks] = vs
            out.append((eid, item))
            last_id = eid
        return out, last_id
    except Exception as exc:
        log.warning("xread failed: %s", exc)
        time.sleep(1)
        return [], last_id
