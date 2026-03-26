from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from app.core.responses import response_success
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest
from app.services.auth import AuthService
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(payload.name, payload.email, payload.password)
    db.commit()
    return response_success({"id": user.id, "email": user.email}, {"request_id": request.state.request_id})


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    access_token, refresh_token = service.login(payload.email, payload.password)
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


@router.post("/logout")
def logout(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.logout(payload.refresh_token)
    db.commit()
    return response_success({}, {"request_id": request.state.request_id})
