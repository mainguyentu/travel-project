# Frontend — Alats Travel DaNang (rewrite MVP, Laravel 11 + Blade)

Contract: `documents/contracts/FE-1.0.0-MVP.md`.

## Chạy dev

```bash
cd frontend
composer install
cp .env.example .env
php artisan key:generate
```

Trỏ `API_BASE_URL` trong `.env` về backend (mặc định `http://127.0.0.1:8001/api/v1`).

```bash
php artisan serve --port=8000
```

## Test

```bash
cd frontend
php artisan test
```

## Luồng chính

- `/` landing (highlights/top từ `public/landing`)
- `/destinations` + popup chi tiết (JS fetch `GET /api/v1/destinations/{id}`, render an toàn không innerHTML)
- `/login`, `/register`, `/profile`, `/my-favorites`, `POST|DELETE /favorites/{id}`, `PUT /ratings/{id}`
- `/admin/*` (dashboard, users, categories, destinations, stats) — guard `session.admin`, role probe qua `admin/stats/top-views`
