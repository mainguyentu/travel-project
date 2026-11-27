# Assessment — P3 integration complete (2026-11-27)

- Requirements: B1/B2 boundaries (browser ↔ frontend `/`, frontend ↔ backend
  `/api/v1/*` qua gateway), `docker-compose.yml` + `nginx.conf` MVP monolith.
  Contract `BE-API-1.0.0-MVP` + `FE-1.0.0-MVP`. WDES 0.1.0, Approved.
- Verification (đã chạy):
  - `docker compose config` → hợp lệ ✅
  - `docker compose up -d` → 5 services Up (postgres healthy, redis healthy,
    backend, frontend, api-gateway) ✅
  - Backend tests trong container compose: `pytest tests/` → **10 passed** ✅
  - Frontend tests local: `php vendor/bin/phpunit` → **11 passed, 34 assertions** ✅
  - `scripts/smoke_p3.py` qua gateway :8080 → **5/5** ✅
    (gateway-health, /health ok, landing 4 keys, home Blade có brand,
    admin login `expires_in=30`)
- Outcome: **Conforms** — P3 tích hợp hoàn thiện.
- Fixes trong P3 (đã áp vào code, không chỉ workaround):
  1. `backend/requirements.txt` += `email-validator==2.2.0` (pydantic EmailStr).
  2. `passlib[bcrypt]` → `bcrypt==4.1.3` trực tiếp (passlib hỏng với bcrypt ≥4.1).
  3. `frontend/Dockerfile`: `php:8.3` → `php:8.4-apache` (lock cần PHP ≥8.4)
     + `chown www-data storage bootstrap/cache`.
  4. `frontend/.dockerignore` mới (loại `vendor/`, context 2GB → 6kB).
  5. `docker-compose.yml` frontend += `APP_KEY`, `APP_NAME`, `ASSET_URL`.
  6. `nginx.conf`: `location = /` trả text → đổi thành `/gateway-health`,
     trả `/` về cho frontend (B1).
  7. `scripts/smoke_p3.py::t_gateway_root` đọc text thay vì JSON.
