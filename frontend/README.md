# Frontend - Travel Project

Frontend sử dụng Laravel Blade SSR để cung cấp giao diện public, user và admin; dữ liệu được lấy qua API gateway.

Cập nhật: 2026-04-24

## 1. Vai trò frontend

- Public pages cho khám phá điểm đến.
- User pages cho profile, favorites và ratings.
- Admin pages cho quản trị users/categories/destinations/stats.

Trong Docker Compose:

- UI chạy trên service frontend tại http://localhost.
- API gateway tại http://localhost:8080 (chỉ phục vụ API và docs).

## 2. Tech stack

- PHP ^8.3
- Laravel ^13
- Vite ^8
- Tailwind CSS ^4

## 3. Cấu trúc chính

- `app/Http/Controllers`: xử lý request web.
- `app/Services/ApiClient.php`: bridge gọi backend API.
- `resources/views`: templates Blade.
- `routes/web.php`: route UI.
- `config/api.php`: config endpoint backend + cache + timeout.

## 4. Route map UI

Public:

- `GET /`
- `GET /destinations`

Auth (guest):

- `GET /login`, `POST /login`
- `GET /register`, `POST /register`

User (session.auth):

- `POST /logout`
- `GET /profile`
- `GET /my-favorites`
- `POST /favorites/{destinationId}`
- `DELETE /favorites/{destinationId}`
- `PUT /ratings/{destinationId}`

Admin (session.admin, prefix /admin):

- `GET /admin`
- `GET /admin/users`
- `PATCH /admin/users/{userId}/status`
- `PATCH /admin/users/{userId}/role`
- `GET /admin/categories`
- `POST /admin/categories`
- `PUT /admin/categories/{categoryId}`
- `DELETE /admin/categories/{categoryId}`
- `GET /admin/destinations`
- `POST /admin/destinations`
- `PUT /admin/destinations/{destinationId}`
- `DELETE /admin/destinations/{destinationId}`
- `GET /admin/stats`

Lưu ý quan trọng:

- Trang destinations hiển thị chi tiết theo popup JavaScript, không dùng route detail riêng.
- Popup gọi `GET /api/v1/destinations/{id}`; payload detail đã gồm insight và metrics.

## 5. Cấu hình API

Biến trong env/frontend config:

- `API_BASE_URL` (mặc định http://localhost:8080)
- `API_VERSION` (mặc định v1)
- `API_TIMEOUT`
- `API_VERIFY_SSL`

ApiClient sẽ tạo URL dạng `/api/{version}/{path}`.

Ví dụ:

- `auth/login` -> `/api/v1/auth/login`
- `destinations` -> `/api/v1/destinations`
- `analytics/summary` -> `/api/v1/analytics/summary`

### 5.1 Cache response

ApiClient hỗ trợ cache GET qua config:

- `API_CACHE_STORE` (khuyến nghị redis)
- `API_CACHE_ENABLED`
- `API_CACHE_TTL`
- `API_CACHE_TTL_LANDING`
- `API_CACHE_TTL_DESTINATIONS`
- `API_CACHE_TTL_ADMIN_STATS`
- `API_CACHE_INVALIDATE_ON_WRITE`
- `API_CACHE_AUTHENTICATED`

### 5.2 Tự động refresh token

- Khi request bị `401` (ngoài `auth/*`), client sẽ thử `POST /api/v1/auth/refresh`.
- Thành công: retry request 1 lần.
- Thất bại: clear token trong session.

## 6. Chạy frontend local

1) Cài đặt:

```bash
cd frontend
composer install
npm install
```

2) Tạo env:

```bash
cp .env.example .env
php artisan key:generate
```

PowerShell:

```powershell
Copy-Item .env.example .env
php artisan key:generate
```

3) Chạy dev:

Terminal 1:

```bash
php artisan serve
```

Terminal 2:

```bash
npm run dev
```

UI local: http://127.0.0.1:8000

## 7. Chạy frontend với full stack

Từ root:

```bash
docker compose up --build
```

UI: http://localhost

API docs: http://localhost:8080/api-docs

Nếu chạy frontend riêng, đảm bảo backend/gateway đã sẵn sàng trước.

## 8. Build và test

Test:

```bash
php artisan test
```

Hoặc:

```bash
composer run test
```

Build assets:

```bash
npm run build
```

## 9. Tài liệu liên quan

- `../README.md`
- `../backend/README.md`
- `../backend/docs/API_REFERENCE.md`
- `../backend/docs/ARCHITECTURE.md`
- `../backend/docs/DEPLOYMENT_RUNBOOK.md`
- `../design-docs/README.md`
- `../DOCKER_INTEGRATION.md`

## 10. Quy ước phát triển

- Giữ controller mỏng; đặt logic API call trong ApiClient.
- Route naming theo domain để map với backend contract.
- Mỗi thay đổi contract backend cần cập nhật đồng thời:
  - `app/Services/ApiClient.php`
  - controllers/views liên quan
  - tài liệu README này nếu thay đổi behavior
