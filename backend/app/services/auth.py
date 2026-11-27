from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.core.config import settings
from app.db.models import User, UserToken


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, name: str, email: str, password: str) -> User:
        exists = self.db.scalar(select(User).where(User.email == email))
        if exists:
            raise AppError("CONFLICT", "Email already registered", 409)
        user = User(name=name, email=email, password_hash=hash_password(password))
        self.db.add(user)
        self.db.flush()
        return user

    def _issue_pair(self, user: User) -> dict:
        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        self.db.add(UserToken(user_id=user.id, token_access=access, refresh_token=refresh))
        self.db.flush()
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "Bearer",
            "expires_in": settings.jwt_access_ttl_min,
        }

    def login(self, email: str, password: str) -> dict:
        user = self.db.scalar(select(User).where(User.email == email))
        if not user or not verify_password(password, user.password_hash):
            raise AppError("UNAUTHORIZED", "Invalid email or password", 401)
        if user.status != "active":
            raise AppError("FORBIDDEN", "User is locked", 403)
        return self._issue_pair(user)

    def refresh(self, refresh_token: str) -> dict:
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise AppError("UNAUTHORIZED", "Invalid or expired refresh token", 401)
        if payload.get("type") != "refresh":
            raise AppError("UNAUTHORIZED", "Invalid token type", 401)
        record = self.db.scalar(
            select(UserToken).where(
                UserToken.refresh_token == refresh_token,
                UserToken.revoked_at.is_(None),
            )
        )
        if not record:
            raise AppError("UNAUTHORIZED", "Refresh token revoked", 401)
        user = self.db.get(User, int(payload["sub"]))
        if not user or user.status != "active":
            raise AppError("UNAUTHORIZED", "User unavailable", 401)
        from datetime import datetime, timezone

        record.revoked_at = datetime.now(timezone.utc)
        return self._issue_pair(user)

    def logout(self, refresh_token: str) -> None:
        record = self.db.scalar(select(UserToken).where(UserToken.refresh_token == refresh_token))
        if record and record.revoked_at is None:
            from datetime import datetime, timezone

            record.revoked_at = datetime.now(timezone.utc)
