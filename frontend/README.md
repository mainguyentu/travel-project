# Frontend - Travel Project

Frontend được xây dựng bằng Laravel (Blade + SSR) và tích hợp với backend thông qua API gateway.
Trong Docker Compose đầy đủ, UI chạy ở service `frontend` riêng trên `http://localhost`, còn `api-gateway` chỉ phục vụ API và docs.
Trang destinations sử dụng popup chi tiết do JavaScript render, thay vì một route chi tiết riêng.

Frontend là lớp giao diện chính của Travel Project, phục vụ cả public flow lẫn admin flow thông qua backend API `/api/v1/*`.

Mục tiêu:

- Public pages cho khám phá địa điểm.
- User pages cho hồ sơ, yêu thích và đánh giá.
- Admin pages cho quản trị users, categories, destinations và stats.

## 1. Tech Stack

- PHP `^8.3`
- Laravel `^13`
- Vite `^8`
- Tailwind CSS `^4`
- Axios/Guzzle để gọi API backend

## 2. Cấu Trúc Thư Mục Chính

- `app/Http/Controllers/`: điều phối request UI và gọi API backend.
- `app/Services/ApiClient.php`: HTTP client gọi backend (`/api/v1/*`).
- `resources/views/`: Blade templates cho public, user và admin.
- `routes/web.php`: toàn bộ route UI.
- `config/api.php`: cấu hình endpoint backend.

## 3. Route Map UI

### Public

- `GET /`
- `GET /destinations`

Ghi chú luồng chi tiết destination:

- Người dùng xem chi tiết ngay tại trang `GET /destinations` thông qua popup.
- Popup gọi trực tiếp API `GET /api/v1/destinations/{destinationId}` bằng JavaScript để lấy dữ liệu chi tiết.
- Payload chi tiết hiện tại có thêm `insight` và `metrics` để hiển thị phần thông tin nâng cao trong modal.
- Không còn route UI riêng cho `GET /destinations/{destinationId}`.

### Auth (guest)

- `GET /login`, `POST /login`
- `GET /register`, `POST /register`

### User (middleware `session.auth`)

- `POST /logout`
- `GET /profile`
- `GET /my-favorites`
- `POST /favorites/{destinationId}`
- `DELETE /favorites/{destinationId}`
- `PUT /ratings/{destinationId}`

### Admin (middleware `session.admin`, prefix `/admin`)

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

## 4. Cấu Hình API Backend

Frontend gọi backend qua `config/api.php`:

- `API_BASE_URL` (mặc định `http://localhost:8080`)
- `API_VERSION` (mặc định `v1`)
- `API_TIMEOUT`
- `API_VERIFY_SSL`

Mặc định `ApiClient` gọi endpoint theo mẫu:

- `/api/{version}/{path}`

Ví dụ:

- `auth/login` -> `/api/v1/auth/login`
- `destinations` -> `/api/v1/destinations`
- `analytics/summary` -> `/api/v1/analytics/summary`

### 4.1 Redis response cache cho frontend

`ApiClient` hỗ trợ cache response cho các request `GET` theo cấu hình trong `config/api.php`.

- Store: `API_CACHE_STORE` (khuyến nghị `redis`)
- Bật/tắt: `API_CACHE_ENABLED`
- TTL mặc định: `API_CACHE_TTL`
- TTL theo path:
  - `API_CACHE_TTL_LANDING`
  - `API_CACHE_TTL_DESTINATIONS`
  - `API_CACHE_TTL_ADMIN_STATS`
- Invalidate cache sau request ghi (`POST/PUT/DELETE`): `API_CACHE_INVALIDATE_ON_WRITE`

Mặc định cache áp dụng cho endpoint public (`public/*`, `destinations*`) và không cache request có token để tránh lưu dữ liệu cá nhân (`API_CACHE_AUTHENTICATED=false`).

### 4.2 Tự Động Refresh Token

`ApiClient` hỗ trợ tự động refresh token:

- Nếu request API trả về `401` và request không nằm trong `auth/*`, client sẽ thử gọi `POST /api/v1/auth/refresh` bằng `refresh_token` trong session.
- Nếu refresh thành công, request gốc được retry một lần.
- Nếu refresh thất bại, session auth (`access_token`, `refresh_token`, `user`) sẽ bị xoá.

## 5. Chạy Local

### 5.1 Cài Đặt

```bash
cd frontend
composer install
npm install
```

Tạo `.env`:

```bash
cp .env.example .env
php artisan key:generate
```

PowerShell:

```powershell
Copy-Item .env.example .env
php artisan key:generate
```

### 5.2 Chạy Dev

Terminal 1:

```bash
php artisan serve
```

Terminal 2:

```bash
npm run dev
```

Mặc định UI: `http://127.0.0.1:8000`

Khi chạy full Docker stack, UI đi qua service frontend tại `http://localhost` (host port 80).

### 5.3 Kiểm Tra Kết Nối API Nhanh

Đảm bảo backend stack đang chạy qua gateway (`http://localhost:8080`), sau đó truy cập:

- Landing page: `GET /`
- Destinations page: `GET /destinations`
- Login page: `GET /login`
- API docs portal: `http://localhost:8080/api-docs`

## 6. Build và Test

Chạy test:

```bash
php artisan test
```

Hoặc:

```bash
composer run test
```

Build assets (local/CI):

```bash
npm run build
```

## 7. Luồng Xác Thực Hiện Tại

- Login/Register gọi backend auth API.
- `access_token` và `refresh_token` được lưu trong session Laravel.
- `ApiClient` tự gắn header Authorization khi có token trong session.
- Khi token hết hạn, `ApiClient` tự refresh và retry một lần.
- Logout gọi `auth/logout` và xoá session token phía frontend.

## 8. Tích Hợp Với Backend

Khuyến nghị chạy bằng Docker Compose từ root project:

```bash
cd ..
docker compose up --build
```

Sau khi stack lên, mở UI ở `http://localhost` và API docs ở `http://localhost:8080/api-docs`.

Nếu muốn chạy frontend riêng, hãy chạy backend/gateway từ root project trước:

```bash
cd ..
docker compose up --build api-gateway
```

Sau đó quay lại frontend để chạy UI local như mục 5.

Nếu cần chỉnh endpoint backend cho môi trường khác, cập nhật `API_BASE_URL` trong `.env` của frontend.

Tài liệu backend liên quan:

- `../backend/README.md`
- `../backend/docs/API_REFERENCE.md`
- `../backend/docs/ARCHITECTURE.md`
- `../backend/docs/DEPLOYMENT_RUNBOOK.md`

Tài liệu hệ thống liên quan:

- `../README.md`
- `../DOCKER_INTEGRATION.md`
- `../design-docs/README.md`

Tài liệu API interactive:

- `http://localhost:8080/api-docs`
- `http://localhost:8080/api-docs/swagger/admin`
- `http://localhost:8080/api-docs/redoc/admin`

## 9. Ghi Chú Phát Triển

- Ưu tiên tách logic gọi API ở `ApiClient` và giữ controller mỏng.
- Giữ route naming nhất quán theo domain (`destinations`, `favorites`, `admin.*`).
- Khi thay đổi contract API backend, cập nhật đồng thời:
  - `app/Services/ApiClient.php`
  - controller liên quan
  - README này nếu thay đổi behavior
