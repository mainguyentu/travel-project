from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.db.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        return self.db.execute(stmt).scalar_one_or_none()

    def list(self, offset: int, limit: int):
        stmt = select(User).offset(offset).limit(limit)
        return self.db.execute(stmt).scalars().all()

    def count(self) -> int:
        stmt = select(func.count(User.id))
        return self.db.execute(stmt).scalar_one()

    def create(self, name: str, email: str, password_hash: str) -> User:
        user = User(name=name, email=email, password_hash=password_hash)
        self.db.add(user)
        self.db.flush()
        return user

    def update_status(self, user: User, status: str) -> User:
        user.status = status
        self.db.flush()
        return user

    def update_role(self, user: User, role: str) -> User:
        user.role = role
        self.db.flush()
        return user
