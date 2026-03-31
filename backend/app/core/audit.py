from __future__ import annotations

import logging
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.db.models import AuditLog

logger = logging.getLogger(__name__)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def write_audit_log(
    db: Session,
    request: Request,
    action: str,
    *,
    actor_user_id: int | None = None,
    actor_email: str | None = None,
    actor_role: str | None = None,
    target_type: str | None = None,
    target_id: str | int | None = None,
    payload: dict[str, Any] | None = None,
    status: str = "success",
) -> None:
    try:
        db.add(
            AuditLog(
                actor_user_id=actor_user_id,
                actor_email=actor_email,
                actor_role=actor_role,
                action=action,
                target_type=target_type,
                target_id=str(target_id) if target_id is not None else None,
                status=status,
                request_id=getattr(request.state, "request_id", None),
                method=request.method,
                path=str(request.url.path),
                ip_address=_client_ip(request),
                user_agent=request.headers.get("user-agent"),
                payload=payload,
            )
        )
        db.flush()
    except Exception as exc:
        logger.warning("Audit log write failed action=%s error=%s", action, exc)
