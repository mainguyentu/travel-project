from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.responses import response_success
from app.db.session import get_db
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
def register(payload: RegisterRequest, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    user = service.register(payload.name, payload.email, payload.password)
    db.commit()
    return response_success(
        {"id": user.id, "name": user.name, "email": user.email},
        {"request_id": request.state.request_id},
    )


@router.post("/login")
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    pair = service.login(payload.email, payload.password)
    db.commit()
    return response_success(pair, {"request_id": request.state.request_id})


@router.post("/refresh")
def refresh(payload: RefreshRequest, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    pair = service.refresh(payload.refresh_token)
    db.commit()
    return response_success(pair, {"request_id": request.state.request_id})


@router.post("/logout")
def logout(payload: LogoutRequest, request: Request, db: Session = Depends(get_db)):
    service = AuthService(db)
    service.logout(payload.refresh_token)
    db.commit()
    return response_success({}, {"request_id": request.state.request_id})
