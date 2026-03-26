from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.core.responses import response_success
from app.core.errors import AppError
from app.core.deps import require_admin
from app.db.session import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.destination import DestinationCreate, DestinationUpdate
from app.schemas.user import UserRoleUpdate, UserStatusUpdate
from app.repositories.categories import CategoryRepository
from app.repositories.destinations import DestinationRepository
from app.repositories.users import UserRepository
from app.services.destinations import DestinationService
from app.services.admin import AdminService
from app.utils.serializers import category_to_dict, destination_to_dict, user_to_dict
from app.core.cache import cache_get, cache_set, key_admin_top, invalidate_admin_stats_cache, invalidate_list_cache, invalidate_public_landing_cache

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/users")
def list_users(request: Request, page: int = Query(default=1, ge=1), limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    repo = UserRepository(db)
    users = repo.list(offset, limit)
    total = repo.count()
    data = [user_to_dict(u) for u in users]
    meta = {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total}
    return response_success(data, meta)


@router.patch("/users/{user_id}/status")
def update_user_status(user_id: int, payload: UserStatusUpdate, request: Request, db: Session = Depends(get_db)):
    service = AdminService(db)
    user = service.update_user_status(user_id, payload.status)
    db.commit()
    return response_success(user_to_dict(user), {"request_id": request.state.request_id})


@router.patch("/users/{user_id}/role")
def update_user_role(user_id: int, payload: UserRoleUpdate, request: Request, db: Session = Depends(get_db)):
    service = AdminService(db)
    user = service.update_user_role(user_id, payload.role)
    db.commit()
    return response_success(user_to_dict(user), {"request_id": request.state.request_id})


@router.get("/categories")
def list_categories(request: Request, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    data = [category_to_dict(c) for c in repo.list()]
    return response_success(data, {"request_id": request.state.request_id})


@router.post("/categories", status_code=201)
def create_category(payload: CategoryCreate, request: Request, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    if repo.get_by_slug(payload.slug):
        raise AppError("CONFLICT", "Slug already exists", status_code=409)
    category = repo.create(payload.name, payload.slug, payload.descriptions)
    db.commit()
    invalidate_list_cache()
    invalidate_public_landing_cache()
    return response_success(category_to_dict(category), {"request_id": request.state.request_id})


@router.put("/categories/{category_id}")
def update_category(category_id: int, payload: CategoryUpdate, request: Request, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    category = repo.get_by_id(category_id)
    if not category:
        raise AppError("NOT_FOUND", "Category not found", status_code=404)
    if payload.slug:
        existing = repo.get_by_slug(payload.slug)
        if existing and existing.id != category_id:
            raise AppError("CONFLICT", "Slug already exists", status_code=409)
    category = repo.update(category, payload.model_dump(exclude_unset=True))
    db.commit()
    invalidate_list_cache()
    invalidate_public_landing_cache()
    return response_success(category_to_dict(category), {"request_id": request.state.request_id})


@router.delete("/categories/{category_id}")
def delete_category(category_id: int, request: Request, db: Session = Depends(get_db)):
    repo = CategoryRepository(db)
    category = repo.get_by_id(category_id)
    if category:
        repo.delete(category)
        db.commit()
        invalidate_list_cache()
        invalidate_public_landing_cache()
    return response_success({}, {"request_id": request.state.request_id})


@router.get("/destinations")
def list_destinations(request: Request, status: str | None = None, page: int = Query(default=1, ge=1), limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    offset = (page - 1) * limit
    repo = DestinationRepository(db)
    items = repo.list_admin(status, offset, limit)
    total = repo.count_admin(status)
    data = [destination_to_dict(d) for d in items]
    meta = {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total}
    return response_success(data, meta)


@router.post("/destinations", status_code=201)
def create_destination(payload: DestinationCreate, request: Request, db: Session = Depends(get_db)):
    service = DestinationService(db)
    data = payload.model_dump(exclude={"category_ids"})
    destination = service.create(data, payload.category_ids)
    db.commit()
    return response_success(destination_to_dict(destination), {"request_id": request.state.request_id})


@router.put("/destinations/{destination_id}")
def update_destination(destination_id: int, payload: DestinationUpdate, request: Request, db: Session = Depends(get_db)):
    service = DestinationService(db)
    data = payload.model_dump(exclude_unset=True, exclude={"category_ids"})
    destination = service.update(destination_id, data, payload.category_ids)
    db.commit()
    return response_success(destination_to_dict(destination), {"request_id": request.state.request_id})


@router.delete("/destinations/{destination_id}")
def delete_destination(destination_id: int, request: Request, db: Session = Depends(get_db)):
    service = DestinationService(db)
    service.delete(destination_id)
    db.commit()
    return response_success({}, {"request_id": request.state.request_id})


@router.get("/stats/top-favorites")
def stats_top_favorites(request: Request, db: Session = Depends(get_db)):
    cache_key = key_admin_top("favorites")
    cached = cache_get(cache_key)
    if cached:
        return response_success(cached, {"request_id": request.state.request_id})
    repo = DestinationRepository(db)
    items = repo.top_by_favorites(limit=10)
    data = [destination_to_dict(d) for d in items]
    cache_set(cache_key, data)
    return response_success(data, {"request_id": request.state.request_id})


@router.get("/stats/top-ratings")
def stats_top_ratings(request: Request, db: Session = Depends(get_db)):
    cache_key = key_admin_top("ratings")
    cached = cache_get(cache_key)
    if cached:
        return response_success(cached, {"request_id": request.state.request_id})
    repo = DestinationRepository(db)
    items = repo.top_by_rating(limit=10)
    data = [destination_to_dict(d) for d in items]
    cache_set(cache_key, data)
    return response_success(data, {"request_id": request.state.request_id})


@router.get("/stats/top-views")
def stats_top_views(request: Request, db: Session = Depends(get_db)):
    cache_key = key_admin_top("views")
    cached = cache_get(cache_key)
    if cached:
        return response_success(cached, {"request_id": request.state.request_id})
    repo = DestinationRepository(db)
    items = repo.top_by_views(limit=10)
    data = [destination_to_dict(d) for d in items]
    cache_set(cache_key, data)
    return response_success(data, {"request_id": request.state.request_id})
