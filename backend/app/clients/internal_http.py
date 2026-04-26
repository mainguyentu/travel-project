from __future__ import annotations

from typing import Any

import httpx

from app.core.config import settings
from app.core.errors import AppError


def _extract_error(payload: Any) -> tuple[str, str, list]:
    if not isinstance(payload, dict):
        return ("UPSTREAM_ERROR", "Upstream request failed", [])
    err = payload.get("error")
    if not isinstance(err, dict):
        return ("UPSTREAM_ERROR", "Upstream request failed", [])
    return (
        str(err.get("code") or "UPSTREAM_ERROR"),
        str(err.get("message") or "Upstream request failed"),
        err.get("details") if isinstance(err.get("details"), list) else [],
    )


def internal_request_json(
    method: str,
    *,
    base_url: str,
    path: str,
    headers: dict[str, str] | None = None,
    json: Any | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + path
    timeout = httpx.Timeout(settings.internal_http_timeout_seconds)

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.request(method, url, headers=headers, json=json, params=params)
    except httpx.RequestError as exc:
        raise AppError("UPSTREAM_UNAVAILABLE", f"Upstream unavailable: {exc}", status_code=502) from exc

    try:
        payload = resp.json()
    except Exception:
        payload = None

    if resp.status_code >= 400:
        code, message, details = _extract_error(payload)
        raise AppError(code, message, status_code=resp.status_code, details=details)

    if isinstance(payload, dict) and payload.get("success") is False:
        code, message, details = _extract_error(payload)
        raise AppError(code, message, status_code=502, details=details)

    if not isinstance(payload, dict):
        raise AppError("UPSTREAM_ERROR", "Invalid upstream response", status_code=502)

    return payload

