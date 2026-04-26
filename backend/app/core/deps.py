from dataclasses import dataclass

from fastapi import Depends, Header
from sqlalchemy.orm import Session
from .errors import AppError
from .security import decode_token
from .responses import response_error
from .config import settings
from app.db.session import get_db
from app.repositories.users import UserRepository


def get_request_id(x_request_id: str | None = Header(default=None)) -> str | None:
    return x_request_id


@dataclass(frozen=True)
class TokenUser:
    id: int
    role: str | None = None
    status: str | None = None
    email: str | None = None


def get_current_user(db: Session = Depends(get_db), authorization: str | None = Header(default=None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise AppError("UNAUTHORIZED", "Missing bearer token", status_code=401)
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise AppError("UNAUTHORIZED", "Invalid token", status_code=401)
    if payload.get("type") != "access":
        raise AppError("UNAUTHORIZED", "Invalid token type", status_code=401)
    user_id = payload.get("sub")
    if not user_id:
        raise AppError("UNAUTHORIZED", "Invalid token subject", status_code=401)

    # Phase 2 - API-first boundary: non-auth services must authenticate/authorize
    # via JWT claims without querying the auth write model tables.
    if settings.service_profile not in {"monolith", "auth-service"}:
        role = payload.get("role")
        status = payload.get("status")
        if status == "locked":
            raise AppError("FORBIDDEN", "User locked", status_code=403)
        return TokenUser(id=int(user_id), role=role, status=status)

    repo = UserRepository(db)
    user = repo.get_by_id(int(user_id))
    if not user:
        raise AppError("UNAUTHORIZED", "User not found", status_code=401)
    if user.status == "locked":
        raise AppError("FORBIDDEN", "User locked", status_code=403)
    return user


def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise AppError("FORBIDDEN", "Admin role required", status_code=403)
    return current_user
