from datetime import datetime, timedelta, timezone

import jwt
import bcrypt
import uuid

from .config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def _encode(payload: dict) -> str:
    payload.setdefault("jti", str(uuid.uuid4()))
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_access_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    return _encode({
        "sub": str(user_id),
        "type": "access",
        "iss": settings.jwt_issuer,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_ttl_min),
    })


def create_refresh_token(user_id: int) -> str:
    now = datetime.now(timezone.utc)
    return _encode({
        "sub": str(user_id),
        "type": "refresh",
        "iss": settings.jwt_issuer,
        "iat": now,
        "exp": now + timedelta(days=settings.jwt_refresh_ttl_days),
    })


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], issuer=settings.jwt_issuer)
