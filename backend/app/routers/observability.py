"""Observability endpoints (Pha C): /metrics (Prometheus text) + /ready."""
from __future__ import annotations

import time

from fastapi import APIRouter, Depends, Request
from fastapi.responses import PlainTextResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.responses import response_success
from app.db.session import get_db
from app.services import search as search_svc

router = APIRouter(tags=["observability"])
router.no_prefix = True  # type: ignore[attr-defined] — mount ở /metrics, /ready (không prefix /api/v1)

_started_at = time.monotonic()


@router.get("/metrics", response_class=PlainTextResponse)
def metrics() -> str:
    uptime = time.monotonic() - _started_at
    lines = [
        "# HELP travel_uptime_seconds Seconds since backend process start.",
        "# TYPE travel_uptime_seconds gauge",
        f"travel_uptime_seconds {uptime:.1f}",
        "# HELP travel_rate_limit_ip_per_min Configured IP rate limit.",
        "# TYPE travel_rate_limit_ip_per_min gauge",
        f"travel_rate_limit_ip_per_min {settings.rate_limit_ip_per_min}",
        "# HELP travel_rate_limit_user_per_min Configured user rate limit.",
        "# TYPE travel_rate_limit_user_per_min gauge",
        f"travel_rate_limit_user_per_min {settings.rate_limit_user_per_min}",
    ]
    return "\n".join(lines) + "\n"


@router.get("/ready")
def ready(request: Request, db: Session = Depends(get_db)):
    checks: dict[str, str] = {}
    try:
        db.execute(text("SELECT 1"))
        checks["postgres"] = "ok"
    except Exception as exc:  # pragma: no cover - surfaced as degraded
        checks["postgres"] = f"error: {exc}"
    try:
        import redis as redis_lib

        r = redis_lib.Redis.from_url(settings.redis_url, socket_connect_timeout=2)
        r.ping()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {exc}"
    es = search_svc.get_client()
    checks["elasticsearch"] = "ok" if es is not None else "fallback-db"
    degraded = any(v != "ok" and k != "elasticsearch" or (k == "elasticsearch" and False) for k, v in checks.items())
    ok = checks.get("postgres") == "ok" and checks.get("redis") == "ok"
    data = {"ready": ok, "checks": checks}
    return response_success(data, {"request_id": request.state.request_id})
