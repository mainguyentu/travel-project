from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy.orm import Session
from app.core.audit import write_audit_log
from app.core.responses import response_success
from app.core.errors import AppError
from app.core.deps import require_admin
from app.db.session import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.destination import DestinationBulkCreate, DestinationCreate, DestinationUpdate
from app.schemas.user import UserRoleUpdate, UserStatusUpdate
from app.repositories.categories import CategoryRepository
from app.repositories.destinations import DestinationRepository
from app.repositories.users import UserRepository
from app.services.destinations import DestinationService
from app.services.admin import AdminService
from app.utils.serializers import category_to_dict, destination_to_dict, user_to_dict
from app.core.cache import cache_get, cache_set, key_admin_top, invalidate_list_cache, invalidate_public_landing_cache
from app.core.config import settings
from app.core.events import EventType, build_event
from app.core.kafka_bus import publish_event
from app.clients.internal_http import internal_request_json

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


@router.get("/users")
def list_users(request: Request, page: int = Query(default=1, ge=1), limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    if settings.service_profile == "monolith":
        offset = (page - 1) * limit
        repo = UserRepository(db)
        users = repo.list(offset, limit)
        total = repo.count()
        data = [user_to_dict(u) for u in users]
        meta = {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total}
        return response_success(data, meta)

    headers = {}
    auth = request.headers.get("authorization")
    if auth:
        headers["Authorization"] = auth
    payload = internal_request_json(
        "GET",
        base_url=settings.auth_service_url,
        path=f"{settings.api_prefix}/internal/admin/users",
        headers=headers,
        params={"page": page, "limit": limit},
    )
    data = payload.get("data", [])
    upstream_meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
    total = int(upstream_meta.get("total", 0) or 0)
    meta = {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total}
    return response_success(data, meta)


@router.patch("/users/{user_id}/status")
def update_user_status(
    user_id: int,
    payload: UserStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if settings.service_profile == "monolith":
        service = AdminService(db)
        user = service.update_user_status(user_id, payload.status)
    else:
        headers = {}
        auth = request.headers.get("authorization")
        if auth:
            headers["Authorization"] = auth
        upstream = internal_request_json(
            "PATCH",
            base_url=settings.auth_service_url,
            path=f"{settings.api_prefix}/internal/admin/users/{user_id}/status",
            headers=headers,
            json=payload.model_dump(),
        )
        user = upstream.get("data")
    write_audit_log(
        db,
        request,
        "admin.user_status.update",
        actor_user_id=current_user.id,
        actor_email=getattr(current_user, "email", None),
        actor_role=getattr(current_user, "role", None),
        target_type="user",
        target_id=(user.get("id") if isinstance(user, dict) else user.id),
        payload={"status": payload.status},
    )
    db.commit()
    data = user if isinstance(user, dict) else user_to_dict(user)
    return response_success(data, {"request_id": request.state.request_id})


@router.patch("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    payload: UserRoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if settings.service_profile == "monolith":
        service = AdminService(db)
        user = service.update_user_role(user_id, payload.role)
    else:
        headers = {}
        auth = request.headers.get("authorization")
        if auth:
            headers["Authorization"] = auth
        upstream = internal_request_json(
            "PATCH",
            base_url=settings.auth_service_url,
            path=f"{settings.api_prefix}/internal/admin/users/{user_id}/role",
            headers=headers,
            json=payload.model_dump(),
        )
        user = upstream.get("data")
    write_audit_log(
        db,
        request,
        "admin.user_role.update",
        actor_user_id=current_user.id,
        actor_email=getattr(current_user, "email", None),
        actor_role=getattr(current_user, "role", None),
        target_type="user",
        target_id=(user.get("id") if isinstance(user, dict) else user.id),
        payload={"role": payload.role},
    )
    db.commit()
    data = user if isinstance(user, dict) else user_to_dict(user)
    return response_success(data, {"request_id": request.state.request_id})


@router.get("/categories")
def list_categories(request: Request, db: Session = Depends(get_db)):
    if settings.service_profile == "monolith":
        repo = CategoryRepository(db)
        data = [category_to_dict(c) for c in repo.list()]
        return response_success(data, {"request_id": request.state.request_id})

    headers = {}
    auth = request.headers.get("authorization")
    if auth:
        headers["Authorization"] = auth
    payload = internal_request_json(
        "GET",
        base_url=settings.destination_service_url,
        path=f"{settings.api_prefix}/internal/admin/categories",
        headers=headers,
    )
    return response_success(payload.get("data", []), {"request_id": request.state.request_id})


@router.post("/categories", status_code=201)
def create_category(payload: CategoryCreate, request: Request, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if settings.service_profile == "monolith":
        repo = CategoryRepository(db)
        if repo.get_by_slug(payload.slug):
            raise AppError("CONFLICT", "Slug already exists", status_code=409)
        category = repo.create(payload.name, payload.slug, payload.descriptions)
        db.commit()
        invalidate_list_cache()
        invalidate_public_landing_cache()
        data = category_to_dict(category)
        target_id = category.id
    else:
        headers = {}
        auth = request.headers.get("authorization")
        if auth:
            headers["Authorization"] = auth
        upstream = internal_request_json(
            "POST",
            base_url=settings.destination_service_url,
            path=f"{settings.api_prefix}/internal/admin/categories",
            headers=headers,
            json=payload.model_dump(),
        )
        data = upstream.get("data")
        target_id = data.get("id") if isinstance(data, dict) else None
    write_audit_log(
        db,
        request,
        "admin.category.create",
        actor_user_id=current_user.id,
        actor_email=getattr(current_user, "email", None),
        actor_role=getattr(current_user, "role", None),
        target_type="category",
        target_id=target_id,
        payload=payload.model_dump(),
    )
    db.commit()
    return response_success(data, {"request_id": request.state.request_id})


@router.put("/categories/{category_id}")
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if settings.service_profile == "monolith":
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
        data = category_to_dict(category)
        target_id = category.id
    else:
        headers = {}
        auth = request.headers.get("authorization")
        if auth:
            headers["Authorization"] = auth
        upstream = internal_request_json(
            "PUT",
            base_url=settings.destination_service_url,
            path=f"{settings.api_prefix}/internal/admin/categories/{category_id}",
            headers=headers,
            json=payload.model_dump(exclude_unset=True),
        )
        data = upstream.get("data")
        target_id = data.get("id") if isinstance(data, dict) else category_id
    write_audit_log(
        db,
        request,
        "admin.category.update",
        actor_user_id=current_user.id,
        actor_email=getattr(current_user, "email", None),
        actor_role=getattr(current_user, "role", None),
        target_type="category",
        target_id=target_id,
        payload=payload.model_dump(exclude_unset=True),
    )
    db.commit()
    return response_success(data, {"request_id": request.state.request_id})


@router.delete("/categories/{category_id}")
def delete_category(category_id: int, request: Request, db: Session = Depends(get_db), current_user=Depends(require_admin)):
    if settings.service_profile == "monolith":
        repo = CategoryRepository(db)
        category = repo.get_by_id(category_id)
        if category:
            write_audit_log(
                db,
                request,
                "admin.category.delete",
                actor_user_id=current_user.id,
                actor_email=getattr(current_user, "email", None),
                actor_role=getattr(current_user, "role", None),
                target_type="category",
                target_id=category.id,
            )
            repo.delete(category)
            db.commit()
            invalidate_list_cache()
            invalidate_public_landing_cache()
        return response_success({}, {"request_id": request.state.request_id})

    headers = {}
    auth = request.headers.get("authorization")
    if auth:
        headers["Authorization"] = auth
    internal_request_json(
        "DELETE",
        base_url=settings.destination_service_url,
        path=f"{settings.api_prefix}/internal/admin/categories/{category_id}",
        headers=headers,
    )
    write_audit_log(
        db,
        request,
        "admin.category.delete",
        actor_user_id=current_user.id,
        actor_email=getattr(current_user, "email", None),
        actor_role=getattr(current_user, "role", None),
        target_type="category",
        target_id=category_id,
    )
    db.commit()
    return response_success({}, {"request_id": request.state.request_id})


@router.get("/destinations")
def list_destinations(
    request: Request,
    status: str | None = None,
    keyword: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    if settings.service_profile == "monolith":
        offset = (page - 1) * limit
        repo = DestinationRepository(db)
        items = repo.list_admin(status, keyword, offset, limit)
        total = repo.count_admin(status, keyword)
        data = [destination_to_dict(d) for d in items]
        meta = {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total}
        return response_success(data, meta)

    headers = {}
    auth = request.headers.get("authorization")
    if auth:
        headers["Authorization"] = auth
    payload = internal_request_json(
        "GET",
        base_url=settings.destination_service_url,
        path=f"{settings.api_prefix}/internal/admin/destinations",
        headers=headers,
        params={"status": status, "keyword": keyword, "page": page, "limit": limit},
    )
    data = payload.get("data", [])
    upstream_meta = payload.get("meta", {}) if isinstance(payload, dict) else {}
    total = int(upstream_meta.get("total", 0) or 0)
    meta = {"request_id": request.state.request_id, "page": page, "limit": limit, "total": total}
    return response_success(data, meta)


@router.post("/destinations", status_code=201)
def create_destination(
    payload: DestinationCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if settings.service_profile == "monolith":
        service = DestinationService(db)
        data = payload.model_dump(exclude={"category_ids"})
        destination = service.create(data, payload.category_ids)
        db.commit()
        publish_event(
            settings.kafka_topic_destination,
            build_event(
                EventType.DESTINATION_CREATED,
                {"destination": destination_to_dict(destination)},
                request_id=request.state.request_id,
            ),
        )
        result = destination_to_dict(destination)
        target_id = destination.id
    else:
        headers = {}
        auth = request.headers.get("authorization")
        if auth:
            headers["Authorization"] = auth
        upstream = internal_request_json(
            "POST",
            base_url=settings.destination_service_url,
            path=f"{settings.api_prefix}/internal/admin/destinations",
            headers=headers,
            json=payload.model_dump(),
        )
        result = upstream.get("data")
        target_id = result.get("id") if isinstance(result, dict) else None
    write_audit_log(
        db,
        request,
        "admin.destination.create",
        actor_user_id=current_user.id,
        actor_email=getattr(current_user, "email", None),
        actor_role=getattr(current_user, "role", None),
        target_type="destination",
        target_id=target_id,
        payload=payload.model_dump(),
    )
    db.commit()
    return response_success(result, {"request_id": request.state.request_id})


@router.post("/destinations/bulk", status_code=201)
def create_destinations_bulk(
    payload: DestinationBulkCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if settings.service_profile == "monolith":
        service = DestinationService(db)
        destinations_payload = [item.model_dump(exclude={"category_ids"}) | {"category_ids": item.category_ids} for item in payload.destinations]
        destinations = service.create_many(destinations_payload)
        db.commit()
        publish_event(
            settings.kafka_topic_destination,
            build_event(
                EventType.DESTINATION_CREATED,
                {"destinations": [destination_to_dict(destination) for destination in destinations]},
                request_id=request.state.request_id,
            ),
        )
        data = [destination_to_dict(destination) for destination in destinations]
        target_id = str(len(destinations))
    else:
        headers = {}
        auth = request.headers.get("authorization")
        if auth:
            headers["Authorization"] = auth
        upstream = internal_request_json(
            "POST",
            base_url=settings.destination_service_url,
            path=f"{settings.api_prefix}/internal/admin/destinations/bulk",
            headers=headers,
            json=payload.model_dump(),
        )
        data = upstream.get("data", [])
        target_id = str(len(data)) if isinstance(data, list) else None
    write_audit_log(
        db,
        request,
        "admin.destination.bulk_create",
        actor_user_id=current_user.id,
        actor_email=getattr(current_user, "email", None),
        actor_role=getattr(current_user, "role", None),
        target_type="destination",
        target_id=target_id,
        payload=payload.model_dump(),
    )
    db.commit()
    return response_success(data, {"request_id": request.state.request_id, "count": len(data)})


@router.put("/destinations/{destination_id}")
def update_destination(
    destination_id: int,
    payload: DestinationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if settings.service_profile == "monolith":
        service = DestinationService(db)
        data = payload.model_dump(exclude_unset=True, exclude={"category_ids"})
        destination = service.update(destination_id, data, payload.category_ids)
        db.commit()
        publish_event(
            settings.kafka_topic_destination,
            build_event(
                EventType.DESTINATION_UPDATED,
                {"destination": destination_to_dict(destination)},
                request_id=request.state.request_id,
            ),
        )
        result = destination_to_dict(destination)
        target_id = destination.id
    else:
        headers = {}
        auth = request.headers.get("authorization")
        if auth:
            headers["Authorization"] = auth
        upstream = internal_request_json(
            "PUT",
            base_url=settings.destination_service_url,
            path=f"{settings.api_prefix}/internal/admin/destinations/{destination_id}",
            headers=headers,
            json=payload.model_dump(exclude_unset=True),
        )
        result = upstream.get("data")
        target_id = result.get("id") if isinstance(result, dict) else destination_id
    write_audit_log(
        db,
        request,
        "admin.destination.update",
        actor_user_id=current_user.id,
        actor_email=getattr(current_user, "email", None),
        actor_role=getattr(current_user, "role", None),
        target_type="destination",
        target_id=target_id,
        payload=payload.model_dump(exclude_unset=True),
    )
    db.commit()
    return response_success(result, {"request_id": request.state.request_id})


@router.delete("/destinations/{destination_id}")
def delete_destination(
    destination_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if settings.service_profile == "monolith":
        service = DestinationService(db)
        service.delete(destination_id)
        db.commit()
        publish_event(
            settings.kafka_topic_destination,
            build_event(
                EventType.DESTINATION_DELETED,
                {"destination_id": destination_id},
                request_id=request.state.request_id,
            ),
        )
    else:
        headers = {}
        auth = request.headers.get("authorization")
        if auth:
            headers["Authorization"] = auth
        internal_request_json(
            "DELETE",
            base_url=settings.destination_service_url,
            path=f"{settings.api_prefix}/internal/admin/destinations/{destination_id}",
            headers=headers,
        )
    write_audit_log(
        db,
        request,
        "admin.destination.delete",
        actor_user_id=current_user.id,
        actor_email=getattr(current_user, "email", None),
        actor_role=getattr(current_user, "role", None),
        target_type="destination",
        target_id=destination_id,
    )
    db.commit()
    return response_success({}, {"request_id": request.state.request_id})


@router.get("/stats/top-favorites")
def stats_top_favorites(request: Request, db: Session = Depends(get_db)):
    cache_key = key_admin_top("favorites")
    cached = cache_get(cache_key)
    if cached:
        return response_success(cached, {"request_id": request.state.request_id})
    if settings.service_profile == "monolith":
        repo = DestinationRepository(db)
        items = repo.top_by_favorites(limit=10)
        data = [destination_to_dict(d) for d in items]
    else:
        payload = internal_request_json(
            "GET",
            base_url=settings.analytics_service_url,
            path=f"{settings.api_prefix}/analytics/top-favorites",
            params={"limit": 10},
        )
        data = payload.get("data", [])
    cache_set(cache_key, data)
    return response_success(data, {"request_id": request.state.request_id})


@router.get("/stats/top-ratings")
def stats_top_ratings(request: Request, db: Session = Depends(get_db)):
    cache_key = key_admin_top("ratings")
    cached = cache_get(cache_key)
    if cached:
        return response_success(cached, {"request_id": request.state.request_id})
    if settings.service_profile == "monolith":
        repo = DestinationRepository(db)
        items = repo.top_by_rating(limit=10)
        data = [destination_to_dict(d) for d in items]
    else:
        payload = internal_request_json(
            "GET",
            base_url=settings.analytics_service_url,
            path=f"{settings.api_prefix}/analytics/top-ratings",
            params={"limit": 10},
        )
        data = payload.get("data", [])
    cache_set(cache_key, data)
    return response_success(data, {"request_id": request.state.request_id})


@router.get("/stats/top-views")
def stats_top_views(request: Request, db: Session = Depends(get_db)):
    cache_key = key_admin_top("views")
    cached = cache_get(cache_key)
    if cached:
        return response_success(cached, {"request_id": request.state.request_id})
    if settings.service_profile == "monolith":
        repo = DestinationRepository(db)
        items = repo.top_by_views(limit=10)
        data = [destination_to_dict(d) for d in items]
    else:
        payload = internal_request_json(
            "GET",
            base_url=settings.analytics_service_url,
            path=f"{settings.api_prefix}/analytics/top-views",
            params={"limit": 10},
        )
        data = payload.get("data", [])
    cache_set(cache_key, data)
    return response_success(data, {"request_id": request.state.request_id})
