from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.models import Category


class CategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, category_id: int) -> Category | None:
        return self.db.get(Category, category_id)

    def get_by_slug(self, slug: str) -> Category | None:
        stmt = select(Category).where(Category.slug == slug)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(self):
        stmt = select(Category)
        return self.db.execute(stmt).scalars().all()

    def create(self, name: str, slug: str, descriptions: str | None) -> Category:
        category = Category(name=name, slug=slug, descriptions=descriptions)
        self.db.add(category)
        self.db.flush()
        return category

    def update(self, category: Category, data: dict) -> Category:
        for k, v in data.items():
            setattr(category, k, v)
        self.db.flush()
        return category

    def delete(self, category: Category) -> None:
        self.db.delete(category)
        self.db.flush()
