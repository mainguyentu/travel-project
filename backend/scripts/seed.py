import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.session import SessionLocal
from app.db.models import User
from app.core.security import hash_password


def upsert_user(db, name, email, password, role):
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.name = name
        user.role = role
        user.status = "active"
        user.password_hash = hash_password(password)
        db.flush()
        return user
    user = User(name=name, email=email, password_hash=hash_password(password), role=role, status="active")
    db.add(user)
    db.flush()
    return user


def run():
    db = SessionLocal()
    try:
        admin = upsert_user(db, "Admin", "admin@alats.vn", "Admin@123", "admin")
        user = upsert_user(db, "User", "user@alats.vn", "User@123", "user")

        db.commit()
        print("User seed done")
        print(f"Admin: {admin.email} / Admin@123")
        print(f"User: {user.email} / User@123")
    finally:
        db.close()


if __name__ == "__main__":
    run()
