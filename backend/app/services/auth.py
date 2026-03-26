from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.errors import AppError
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.db.models import UserToken
from app.repositories.users import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)

    def register(self, name: str, email: str, password: str):
        if self.users.get_by_email(email):
            raise AppError("CONFLICT", "Email already exists", status_code=409)
        user = self.users.create(name=name, email=email, password_hash=hash_password(password))
        return user

    def login(self, email: str, password: str):
        user = self.users.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise AppError("UNAUTHORIZED", "Invalid credentials", status_code=401)
        if user.status == "locked":
            raise AppError("FORBIDDEN", "User locked", status_code=403)
        access_token = create_access_token(str(user.id), user.role, user.status)
        refresh_token = create_refresh_token(str(user.id))
        token = UserToken(user_id=user.id, token_access=access_token, refresh_token=refresh_token)
        self.db.add(token)
        self.db.flush()
        return access_token, refresh_token

    def refresh(self, refresh_token: str):
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise AppError("UNAUTHORIZED", "Invalid refresh token", status_code=401)
        if payload.get("type") != "refresh":
            raise AppError("UNAUTHORIZED", "Invalid token type", status_code=401)
        user_id = int(payload.get("sub"))
        stmt = select(UserToken).where(UserToken.refresh_token == refresh_token, UserToken.revoked_at.is_(None))
        token_row = self.db.execute(stmt).scalar_one_or_none()
        if not token_row:
            raise AppError("UNAUTHORIZED", "Refresh token revoked", status_code=401)
        user = self.users.get_by_id(user_id)
        if not user:
            raise AppError("UNAUTHORIZED", "User not found", status_code=401)
        if user.status == "locked":
            raise AppError("FORBIDDEN", "User locked", status_code=403)
        access_token = create_access_token(str(user.id), user.role, user.status)
        new_refresh = create_refresh_token(str(user.id))
        token_row.revoked_at = datetime.now(timezone.utc)
        token = UserToken(user_id=user.id, token_access=access_token, refresh_token=new_refresh)
        self.db.add(token)
        self.db.flush()
        return access_token, new_refresh

    def logout(self, refresh_token: str):
        try:
            payload = decode_token(refresh_token)
        except Exception:
            raise AppError("UNAUTHORIZED", "Invalid refresh token", status_code=401)
        user_id = int(payload.get("sub"))
        stmt = select(UserToken).where(
            UserToken.user_id == user_id,
            UserToken.refresh_token == refresh_token,
            UserToken.revoked_at.is_(None),
        )
        token = self.db.execute(stmt).scalar_one_or_none()
        if token:
            token.revoked_at = datetime.now(timezone.utc)
            self.db.flush()
