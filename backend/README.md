# Backend — Alats Travel DaNang (rewrite MVP, monolith FastAPI)

Contract: `documents/contracts/BE-API-1.0.0-MVP.md`.

## Chạy dev

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # sửa DATABASE_URL nếu cần
alembic upgrade head
python scripts/seed.py
python scripts/seed_catalog.py
uvicorn app.main:app --reload --port 8001
```

Docs tương tác: http://127.0.0.1:8001/docs

## Test

```bash
cd backend
pytest -q
```

## Tài khoản seed

- `admin@alats.vn` / `Admin@123` (role admin)
- `user@alats.vn` / `User@123` (role user)
