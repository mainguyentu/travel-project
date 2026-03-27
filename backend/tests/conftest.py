import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "")

from app.db.base import Base
from app.db.session import engine, SessionLocal
import app.db.models  # noqa: F401


def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def pytest_sessionstart(session):
    reset_db()
