from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.db.models import (
    AuditLog,
    Category,
    CategoryDestination,
    Destination,
    DestinationInsight,
    Favorite,
    Rating,
    User,
)


class AdminService:
    def __init__(self, db: Session):
        self.db = db

    # users
    def list_users(self, offset: int, limit: int) -> tuple[list[User], int]:
        total = int(self.db.scalar(select(func.count()).select_from(User)) or 0)
        items = list(self.db.scalars(select(User).order_by(User.id.asc()).offset(offset).limit(limit)).all())
        return items, total

    def update_user_status(self, user_id: int, status: str) -> User:
        user = self.db.get(User, user_id)
        if not user:
            raise AppError("NOT_FOUND", "User not found", 404)
        user.status = status
        self.db.flush()
        return user

    def update_user_role(self, user_id: int, role: str) -> User:
        user = self.db.get(User, user_id)
        if not user:
            raise AppError("NOT_FOUND", "User not found", 404)
        user.role = role
        self.db.flush()
        return user

    def audit(self, actor_user_id: int | None, action: str, entity: str, entity_id: str | None = None, detail: dict | None = None) -> None:
        self.db.add(AuditLog(
            actor_user_id=actor_user_id, action=action, entity=entity,
            entity_id=entity_id, detail=detail,
        ))
        self.db.flush()

    def _get_category(self, category_id: int) -> Category:
        cat = self.db.get(Category, category_id)
        if not cat:
            raise AppError("NOT_FOUND", "Category not found", 404)
        return cat

    # categories
    def list_categories(self) -> list[Category]:
        return list(self.db.scalars(select(Category).order_by(Category.name.asc())).all())

    def create_category(self, name: str, slug: str, descriptions: str | None) -> Category:
        if self.db.scalar(select(Category).where(Category.slug == slug)):
            raise AppError("CONFLICT", "Category slug exists", 409)
        cat = Category(name=name, slug=slug, descriptions=descriptions)
        self.db.add(cat)
        self.db.flush()
        return cat

    def update_category(self, category_id: int, **fields) -> Category:
        cat = self._get_category(category_id)
        if fields.get("slug") and fields["slug"] != cat.slug:
            if self.db.scalar(select(Category).where(Category.slug == fields["slug"])):
                raise AppError("CONFLICT", "Category slug exists", 409)
        for k, v in fields.items():
            if v is not None:
                setattr(cat, k, v)
        self.db.flush()
        return cat

    def delete_category(self, category_id: int) -> None:
        cat = self._get_category(category_id)
        self.db.query(CategoryDestination).filter_by(category_id=cat.id).delete()
        self.db.delete(cat)
        self.db.flush()

    # destinations
    def _resolve_categories(self, slugs: list[str]) -> list[Category]:
        if not slugs:
            return []
        cats = list(self.db.scalars(select(Category).where(Category.slug.in_(slugs))).all())
        found = {c.slug for c in cats}
        missing = [s for s in slugs if s not in found]
        if missing:
            raise AppError("VALIDATION_ERROR", f"Unknown categories: {', '.join(missing)}", 400)
        return cats

    def list_destinations(self, status: str | None, keyword: str | None, offset: int, limit: int) -> tuple[list[Destination], int]:
        stmt = select(Destination)
        if status:
            stmt = stmt.where(Destination.status == status)
        if keyword:
            like = f"%{keyword}%"
            stmt = stmt.where(or_(Destination.name.ilike(like), Destination.address.ilike(like)))
        total = int(self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0)
        items = list(self.db.scalars(stmt.order_by(Destination.id.desc()).offset(offset).limit(limit)).all())
        return items, total

    def create_destination(self, data: dict) -> Destination:
        if self.db.scalar(select(Destination).where(Destination.slug == data["slug"])):
            raise AppError("CONFLICT", "Destination slug exists", 409)
        slugs = data.pop("category_slugs", [])
        dest = Destination(**data)
        self.db.add(dest)
        self.db.flush()
        cats = self._resolve_categories(slugs)
        for cat in cats:
            self.db.add(CategoryDestination(category_id=cat.id, destination_id=dest.id))
        self.db.add(DestinationInsight(destination_id=dest.id, final_data={"summary": "", "status": "insufficient_data"}))
        self.db.flush()
        self._index_sync(dest, [c.slug for c in cats])
        return dest

    def _index_sync(self, dest: Destination, category_slugs: list[str]) -> None:
        try:
            from app.services import search as search_svc

            search_svc.ensure_index()
            search_svc.index_destination({
                "id": dest.id, "name": dest.name, "slug": dest.slug,
                "address": dest.address or "", "description": dest.description or "",
                "price_level": dest.price_level, "category_slugs": category_slugs,
                "rating_avg": float(dest.rating_avg or 0), "status": dest.status,
            })
        except Exception:
            pass

    def bulk_create_destinations(self, items: list[dict]) -> list[Destination]:
        slugs = [it.get("slug") for it in items]
        dupes = {s for s in slugs if slugs.count(s) > 1}
        if dupes:
            raise AppError("VALIDATION_ERROR", f"Duplicate slug in payload: {', '.join(sorted(dupes))}", 400)
        existing = set(
            self.db.scalars(select(Destination.slug).where(Destination.slug.in_(slugs))).all()
        ) if slugs else set()
        if existing:
            raise AppError("CONFLICT", f"Slug exists: {', '.join(sorted(existing))}", 409)
        created: list[Destination] = []
        created_slugs: list[list[str]] = []
        for data in items:
            category_slugs = data.pop("category_slugs", [])
            dest = Destination(**data)
            self.db.add(dest)
            self.db.flush()
            cats = self._resolve_categories(category_slugs)
            for cat in cats:
                self.db.add(CategoryDestination(category_id=cat.id, destination_id=dest.id))
            self.db.add(DestinationInsight(destination_id=dest.id, final_data={"summary": "", "status": "insufficient_data"}))
            created.append(dest)
            created_slugs.append([c.slug for c in cats])
        self.db.flush()
        for dest, slugs in zip(created, created_slugs):
            self._index_sync(dest, slugs)
        return created

    def update_destination(self, destination_id: int, data: dict) -> Destination:
        dest = self.db.get(Destination, destination_id)
        if not dest:
            raise AppError("NOT_FOUND", "Destination not found", 404)
        slugs = data.pop("category_slugs", None)
        if data.get("slug") and data["slug"] != dest.slug:
            if self.db.scalar(select(Destination).where(Destination.slug == data["slug"])):
                raise AppError("CONFLICT", "Destination slug exists", 409)
        for k, v in data.items():
            if v is not None:
                setattr(dest, k, v)
        if slugs is not None:
            self.db.query(CategoryDestination).filter_by(destination_id=dest.id).delete()
            cats = self._resolve_categories(slugs)
            for cat in cats:
                self.db.add(CategoryDestination(category_id=cat.id, destination_id=dest.id))
        else:
            cats = []
        self.db.flush()
        self._index_sync(dest, [c.slug for c in cats])
        return dest

    def delete_destination(self, destination_id: int) -> None:
        dest = self.db.get(Destination, destination_id)
        if not dest:
            raise AppError("NOT_FOUND", "Destination not found", 404)
        self.db.query(CategoryDestination).filter_by(destination_id=dest.id).delete()
        self.db.delete(dest)
        self.db.flush()
        try:
            from app.services import search as search_svc

            search_svc.remove_destination(destination_id)
        except Exception:
            pass
