"""Rate limiting (Pha C): IP 120/phút, user 60/phút (giữ ngưỡng owner đã chốt).

In-memory sliding window (đủ cho single-replica monolith; ghi chú scale-out
trong runbook). Trả 429 envelope chuẩn khi vượt ngưỡng.
"""
from __future__ import annotations

import time
from collections import deque

from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.responses import response_error

_buckets: dict[str, deque[float]] = {}


def _allow(key: str, limit: int, window: float = 60.0) -> tuple[bool, int]:
    now = time.monotonic()
    dq = _buckets.setdefault(key, deque())
    while dq and dq[0] <= now - window:
        dq.popleft()
    if len(dq) >= limit:
        retry = int(window - (now - dq[0])) + 1
        return False, max(retry, 1)
    dq.append(now)
    return True, 0


def _user_key(request: Request) -> str | None:
    user = getattr(request.state, "current_user", None)
    if user is not None:
        return f"user:{user.id}"
    return None


async def rate_limit_middleware(request, call_next):
    if request.url.path in ("/health", "/api/v1/health"):
        return await call_next(request)
    ip = request.client.host if request.client else "unknown"
    ok, retry = _allow(f"ip:{ip}", settings.rate_limit_ip_per_min)
    if not ok:
        meta = {"request_id": getattr(request.state, "request_id", ""), "retry_after": retry}
        return JSONResponse(
            status_code=429,
            content=response_error("RATE_LIMITED", "Too many requests from this IP", [], meta),
            headers={"Retry-After": str(retry)},
        )
    response = await call_next(request)
    user_key = _user_key(request)
    if user_key:
        ok, retry = _allow(user_key, settings.rate_limit_user_per_min)
        if not ok:
            meta = {"request_id": getattr(request.state, "request_id", ""), "retry_after": retry}
            return JSONResponse(
                status_code=429,
                content=response_error("RATE_LIMITED", "Too many requests for this user", [], meta),
                headers={"Retry-After": str(retry)},
            )
    return response


def reset_buckets() -> None:
    _buckets.clear()
