"""Seed MVP dev accounts. Idempotent."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.security import hash_password
from app.db.models import User
from app.db.session import SessionLocal

ACCOUNTS = [
    ("Admin", "admin@alats.vn", "Admin@123", "admin"),
    ("User", "user@alats.vn", "User@123", "user"),
]


def main() -> None:
    db = SessionLocal()
    try:
        for name, email, password, role in ACCOUNTS:
            if db.query(User).filter_by(email=email).first():
                print(f"skip {email}")
                continue
            db.add(User(name=name, email=email, password_hash=hash_password(password), role=role))
            print(f"created {email}")
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    main()
