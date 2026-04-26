from __future__ import annotations

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.core.deps import require_admin
from app.core.responses import response_success
from app.core.errors import AppError
from app.db.session import get_db
from app.repositories.users import UserRepository
from app.schemas.user import UserRoleUpdate, UserStatusUpdate
from app.utils.serializers import user_to_dict


router = APIRouter(
    prefix="/internal/admin",
    tags=["internal-auth-admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/users")
def list_users(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    offset = (page - 1) * limit
    repo = UserRepository(db)
    users = repo.list(offset, limit)
    total = repo.count()
    data = [user_to_dict(u) for u in users]
    meta = {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total}
    return response_success(data, meta)


@router.patch("/users/{user_id}/status")
def update_user_status(user_id: int, payload: UserStatusUpdate, request: Request, db: Session = Depends(get_db)):
    if payload.status not in {"active", "locked"}:
        raise AppError("VALIDATION_ERROR", "Invalid status", status_code=400)
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise AppError("NOT_FOUND", "User not found", status_code=404)
    user = repo.update_status(user, payload.status)
    db.commit()
    return response_success(user_to_dict(user), {"request_id": request.state.request_id})


@router.patch("/users/{user_id}/role")
def update_user_role(user_id: int, payload: UserRoleUpdate, request: Request, db: Session = Depends(get_db)):
    if payload.role not in {"user", "admin"}:
        raise AppError("VALIDATION_ERROR", "Invalid role", status_code=400)
    repo = UserRepository(db)
    user = repo.get_by_id(user_id)
    if not user:
        raise AppError("NOT_FOUND", "User not found", status_code=404)
    user = repo.update_role(user, payload.role)
    db.commit()
    return response_success(user_to_dict(user), {"request_id": request.state.request_id})

