# Frontend - Travel Project

Frontend được xây dựng bằng Laravel (Blade + SSR) và tích hợp backend thông qua API Gateway.
Trang destinations sử dụng popup chi tiết (render bằng JS) thay cho route chi tiết riêng.

Mục tiêu:

- Public pages cho khám phá điểm đến.
- User pages cho hồ sơ, yêu thích, đánh giá.
- Admin pages cho quản trị users/categories/destinations/stats.

## 1. Tech Stack

- PHP `^8.3`
- Laravel `^13`
- Vite `^8`
- Tailwind CSS `^4`
- Axios/Guzzle cho gọi API backend

## 2. Cấu trúc thư mục chính

- `app/Http/Controllers/`: điều phối request UI và gọi API backend.
- `app/Services/ApiClient.php`: HTTP client gọi backend (`/api/v1/*`).
- `resources/views/`: Blade templates cho public/user/admin.
- `routes/web.php`: toàn bộ route UI.
- `config/api.php`: cấu hình endpoint backend.

## 3. Route map UI

Public:

- `GET /`
- `GET /destinations`

Ghi chú luồng chi tiết destination:

- Người dùng xem chi tiết ngay tại trang `GET /destinations` thông qua popup.
- Popup gọi trực tiếp API `GET /api/v1/destinations/{destinationId}` bằng JavaScript để lấy dữ liệu chi tiết.
- Không còn route UI riêng cho trang `GET /destinations/{destinationId}`.

Auth (guest):

- `GET /login`, `POST /login`
- `GET /register`, `POST /register`

User (middleware `session.auth`):

- `POST /logout`
- `GET /profile`
- `GET /my-favorites`
- `POST /favorites/{destinationId}`
- `DELETE /favorites/{destinationId}`
- `PUT /ratings/{destinationId}`

Admin (middleware `session.admin`, prefix `/admin`):

- `GET /admin`
- `GET /admin/users`
- `GET /admin/categories`
- `GET /admin/destinations`
- `GET /admin/stats`

## 4. Cấu hình API backend

Frontend gọi backend qua config `config/api.php`:

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

`ApiClient` đã hỗ trợ cache response cho các request `GET` theo cấu hình trong `config/api.php`.

- Store: `API_CACHE_STORE` (khuyến nghị `redis`)
- Bật/tắt: `API_CACHE_ENABLED`
- TTL mặc định: `API_CACHE_TTL`
- TTL theo path:
	- `API_CACHE_TTL_LANDING`
	- `API_CACHE_TTL_DESTINATIONS`
	- `API_CACHE_TTL_ADMIN_STATS`
- Invalidate cache sau request ghi (`POST/PUT/DELETE`): `API_CACHE_INVALIDATE_ON_WRITE`

Mặc định cache áp dụng cho endpoint public (`public/*`, `destinations*`) và không cache request có token để tránh cache dữ liệu cá nhân (`API_CACHE_AUTHENTICATED=false`).

## 5. Chạy local

### 5.1 Cài đặt

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

### 5.2 Chạy dev

Terminal 1:

```bash
php artisan serve
```

Terminal 2:

```bash
npm run dev
```

Mặc định UI: `http://127.0.0.1:8000`

### 5.3 Kiểm tra kết nối API nhanh

Đảm bảo backend stack đang chạy qua gateway (`http://localhost:8080`), sau đó truy cập:

- Landing page: `GET /`
- Destinations page: `GET /destinations`
- Login page: `GET /login`

## 6. Build và test

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

## 7. Luồng xác thực hiện tại

- Login/Register gọi backend auth API.
- `access_token` và `refresh_token` lưu trong session Laravel.
- `ApiClient` tự gắn header Authorization khi có token trong session.
- Logout gọi `auth/logout` và xóa session token phía frontend.

## 8. Tích hợp với backend

Khuyến nghị chạy backend bằng Docker Compose từ root project:

```bash
cd ..
docker compose up --build
```

Sau đó quay lại frontend để chạy UI local như mục 5.

Nếu cần chỉnh endpoint backend cho môi trường khác, cập nhật `API_BASE_URL` trong `.env` frontend.

Tài liệu backend liên quan:

- `../backend/README.md`
- `../backend/docs/API_REFERENCE.md`
- `../backend/docs/ARCHITECTURE.md`

## 9. Ghi chú phát triển

- Ưu tiên tách logic gọi API ở `ApiClient` và giữ controller mỏng.
- Giữ route naming nhất quán theo domain (`destinations`, `favorites`, `admin.*`).
- Khi đổi contract API backend, cập nhật đồng thời:
	- `app/Services/ApiClient.php`
	- controller liên quan
	- README này (nếu thay đổi behavior)
