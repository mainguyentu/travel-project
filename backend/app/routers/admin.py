from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin  # noqa: F401  (require_admin used as router guard)
from app.core.responses import response_success
from app.db.session import get_db
from app.repositories.destinations import DestinationRepository
from app.schemas.admin import (
    CategoryCreate,
    CategoryUpdate,
    DestinationBulkCreate,
    DestinationCreate,
    DestinationUpdate,
    UserRoleUpdate,
    UserStatusUpdate,
)
from app.services.admin import AdminService
from app.utils.serializers import category_to_dict, destination_to_dict
from app.services import events as event_bus

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _user_to_dict(u) -> dict:
    return {"id": u.id, "name": u.name, "email": u.email, "role": u.role, "status": u.status}


def _parse(value: str | None):
    if not value:
        return None
    from datetime import datetime

    return datetime.fromisoformat(value.replace("Z", "+00:00"))


@router.get("/users")
def list_users(request: Request, page: int = Query(default=1, ge=1), limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    service = AdminService(db)
    items, total = service.list_users((page - 1) * limit, limit)
    return response_success([_user_to_dict(u) for u in items], {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total})


@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AdminService(db)
    user = service.update_user_status(user_id, payload.status)
    service.audit(current_user.id, "user_status", "user", str(user.id), {"status": payload.status})
    db.commit()
    return response_success(_user_to_dict(user), {"request_id": request.state.request_id})


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AdminService(db)
    user = service.update_user_role(user_id, payload.role)
    service.audit(current_user.id, "user_role", "user", str(user.id), {"role": payload.role})
    db.commit()
    return response_success(_user_to_dict(user), {"request_id": request.state.request_id})


@router.get("/categories")
def list_categories(request: Request, db: Session = Depends(get_db)):
    service = AdminService(db)
    return response_success([category_to_dict(c) for c in service.list_categories()], {"request_id": request.state.request_id})


@router.post("/categories", status_code=201)
def create_category(
    payload: CategoryCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AdminService(db)
    cat = service.create_category(payload.name, payload.slug, payload.descriptions)
    service.audit(current_user.id, "create", "category", str(cat.id), {"slug": cat.slug})
    db.commit()
    return response_success(category_to_dict(cat), {"request_id": request.state.request_id})


@router.put("/categories/{category_id}")
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AdminService(db)
    cat = service.update_category(category_id, **payload.model_dump())
    service.audit(current_user.id, "update", "category", str(cat.id), None)
    db.commit()
    return response_success(category_to_dict(cat), {"request_id": request.state.request_id})


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AdminService(db)
    service.delete_category(category_id)
    service.audit(current_user.id, "delete", "category", str(category_id), None)
    db.commit()
    return response_success({}, {"request_id": request.state.request_id})


@router.get("/destinations")
def list_destinations(
    request: Request,
    status: str | None = None,
    keyword: str | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    service = AdminService(db)
    items, total = service.list_destinations(status, keyword, (page - 1) * limit, limit)
    return response_success([destination_to_dict(d) for d in items], {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total})


@router.post("/destinations", status_code=201)
def create_destination(
    payload: DestinationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AdminService(db)
    dest = service.create_destination(payload.model_dump())
    service.audit(current_user.id, "create", "destination", str(dest.id), {"slug": dest.slug})
    db.commit()
    event_bus.publish("destination.changed", {"destination_id": dest.id})
    return response_success(destination_to_dict(dest), {"request_id": request.state.request_id})


@router.post("/destinations/bulk", status_code=201)
def bulk_create_destinations(
    payload: DestinationBulkCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AdminService(db)
    created = service.bulk_create_destinations([it.model_dump() for it in payload.items])
    db.commit()
    for d in created:
        event_bus.publish("destination.changed", {"destination_id": d.id})
    request_id = request.state.request_id
    service.audit(current_user.id, "bulk_create", "destination", None, {"count": len(created)})
    db.commit()
    return response_success([destination_to_dict(d) for d in created], {"request_id": request_id})


@router.put("/destinations/{destination_id}")
def update_destination(
    destination_id: int,
    payload: DestinationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AdminService(db)
    dest = service.update_destination(destination_id, payload.model_dump())
    service.audit(current_user.id, "update", "destination", str(dest.id), None)
    db.commit()
    event_bus.publish("destination.changed", {"destination_id": dest.id})
    return response_success(destination_to_dict(dest), {"request_id": request.state.request_id})


@router.delete("/destinations/{destination_id}")
def delete_destination(
    destination_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = AdminService(db)
    service.delete_destination(destination_id)
    service.audit(current_user.id, "delete", "destination", str(destination_id), None)
    db.commit()
    return response_success({}, {"request_id": request.state.request_id})


@router.get("/stats/top-favorites")
def top_favorites(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
):
    repo = DestinationRepository(db)
    items = repo.top_favorites(limit, _parse(from_date), _parse(to_date))
    return response_success([destination_to_dict(d) for d in items], {"request_id": request.state.request_id})


@router.get("/stats/top-ratings")
def top_ratings(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    from_date: str | None = Query(default=None, alias="from"),
    to_date: str | None = Query(default=None, alias="to"),
    db: Session = Depends(get_db),
):
    repo = DestinationRepository(db)
    items = repo.top_ratings(limit, _parse(from_date), _parse(to_date))
    return response_success([destination_to_dict(d) for d in items], {"request_id": request.state.request_id})


@router.get("/stats/top-views")
def top_views(request: Request, db: Session = Depends(get_db)):
    repo = DestinationRepository(db)
    return response_success([destination_to_dict(d) for d in repo.top_views(10)], {"request_id": request.state.request_id})


@router.get("/audit-logs")
def list_audit_logs(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    from app.db.models import AuditLog as _AuditLog

    offset = (page - 1) * limit
    total = int(db.scalar(select(func.count()).select_from(_AuditLog)) or 0)
    rows = list(
        db.scalars(select(_AuditLog).order_by(_AuditLog.id.desc()).offset(offset).limit(limit)).all()
    )
    data = [
        {
            "id": r.id, "actor_user_id": r.actor_user_id, "action": r.action,
            "entity": r.entity, "entity_id": r.entity_id, "detail": r.detail,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]
    return response_success(data, {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total})
