from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.audit import write_audit_log
from app.core.responses import response_success
from app.core.security import decode_token
from app.db.session import get_db
from app.repositories.users import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest
from app.services.auth import AuthService
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(payload.name, payload.email, payload.password)
    write_audit_log(
        db,
        request,
        "auth.register",
        actor_user_id=user.id,
        actor_email=user.email,
        actor_role=user.role,
        target_type="user",
        target_id=user.id,
    )
    db.commit()
    return response_success({"id": user.id, "email": user.email}, {"request_id": request.state.request_id})


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    access_token, refresh_token = service.login(payload.email, payload.password)
    token_payload = decode_token(access_token)
    user = UserRepository(db).get_by_id(int(token_payload["sub"]))
    write_audit_log(
        db,
        request,
        "auth.login",
        actor_user_id=user.id if user else None,
        actor_email=user.email if user else payload.email,
        actor_role=user.role if user else token_payload.get("role"),
        target_type="user",
        target_id=token_payload.get("sub"),
    )
    db.commit()
    return response_success(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.jwt_access_ttl_min * 60,
        },
        {"request_id": request.state.request_id},
    )


@router.post("/refresh")
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    access_token, refresh_token = service.refresh(payload.refresh_token)
    token_payload = decode_token(access_token)
    user = UserRepository(db).get_by_id(int(token_payload["sub"]))
    write_audit_log(
        db,
        request,
        "auth.refresh",
        actor_user_id=user.id if user else None,
        actor_email=user.email if user else None,
        actor_role=user.role if user else token_payload.get("role"),
        target_type="user",
        target_id=token_payload.get("sub"),
    )
    db.commit()
    return response_success(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "Bearer",
            "expires_in": settings.jwt_access_ttl_min,
        },
        {"request_id": request.state.request_id},
    )


@router.post("/logout")
def logout(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.logout(payload.refresh_token)
    token_payload = decode_token(payload.refresh_token)
    user = UserRepository(db).get_by_id(int(token_payload["sub"]))
    write_audit_log(
        db,
        request,
        "auth.logout",
        actor_user_id=user.id if user else None,
        actor_email=user.email if user else None,
        actor_role=user.role if user else None,
        target_type="user",
        target_id=token_payload.get("sub"),
    )
    db.commit()
    return response_success({}, {"request_id": request.state.request_id})
