from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import decode_token
from app.db.models import User
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if not credentials or not credentials.credentials:
        raise AppError("UNAUTHORIZED", "Missing credentials", 401)
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise AppError("UNAUTHORIZED", "Invalid or expired token", 401)
    if payload.get("type") != "access":
        raise AppError("UNAUTHORIZED", "Invalid token type", 401)
    user = db.get(User, int(payload["sub"]))
    if not user:
        raise AppError("UNAUTHORIZED", "User not found", 401)
    if user.status != "active":
        raise AppError("FORBIDDEN", "User is locked", 403)
    request.state.current_user = user
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise AppError("FORBIDDEN", "Admin only", 403)
    return current_user
