from sqlalchemy.orm import Session
from app.core.errors import AppError
from app.repositories.users import UserRepository
from app.repositories.categories import CategoryRepository
from app.repositories.destinations import DestinationRepository


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.users = UserRepository(db)
        self.categories = CategoryRepository(db)
        self.destinations = DestinationRepository(db)

    def update_user_status(self, user_id: int, status: str):
        if status not in {"active", "locked"}:
            raise AppError("VALIDATION_ERROR", "Invalid status", status_code=400)
        user = self.users.get_by_id(user_id)
        if not user:
            raise AppError("NOT_FOUND", "User not found", status_code=404)
        return self.users.update_status(user, status)

    def update_user_role(self, user_id: int, role: str):
        if role not in {"user", "admin"}:
            raise AppError("VALIDATION_ERROR", "Invalid role", status_code=400)
        user = self.users.get_by_id(user_id)
        if not user:
            raise AppError("NOT_FOUND", "User not found", status_code=404)
        return self.users.update_role(user, role)
