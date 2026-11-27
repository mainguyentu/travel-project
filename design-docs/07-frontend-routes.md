# 07 - Frontend Routes

> Lưu ý (theo code hiện tại `frontend/routes/web.php`):
> **Không có** route `GET /destinations/{destinationId}` riêng —
> chi tiết destination hiển thị bằng **popup/modal JS** trên trang danh sách,
> popup gọi trực tiếp `GET /api/v1/destinations/{id}` (gồm insight + metrics).
> **Không có** route `GET /admin/login` riêng — admin dùng chung form `/login`,
> role được suy ra bằng cách probe `GET /api/v1/admin/stats/top-views` sau login.

## 1. Public routes

- `GET /` - Landing page
- `GET /destinations` - Danh sách địa điểm (+ popup chi tiết, không route riêng)
- `GET /login` - Đăng nhập
- `GET /register` - Đăng ký
- `GET /profile` - Hồ sơ user
- `GET /my-favorites` - Danh sách yêu thích của user

## 2. Admin routes (UI)

- `GET /admin` - Dashboard
- `GET /admin/users` - Quản lý user
- `GET /admin/categories` - Quản lý category
- `GET /admin/destinations` - Quản lý destination
- `GET /admin/stats` - Thống kê tổng hợp

> Không có `GET /admin/login` (theo code hiện tại).

## 3. Route guard

- Public: mở cho Guest.
- User-only (`session.auth`): `POST /logout`, `GET /profile`, `GET /my-favorites`,
  `POST|DELETE /favorites/{id}`, `PUT /ratings/{id}` yêu cầu auth.
- Admin-only (`session.admin`, prefix `/admin`): tất cả route `/admin/*` yêu cầu role admin
  (role do backend probe sau login, không có trang login admin riêng).

## 4. Route naming (Laravel — theo code hiện tại)

### 4.1 Public
- `home` (`GET /`)
- `destinations.index` (`GET /destinations`)
- `login` / `register` (`GET /login`, `GET /register`, middleware `guest`)
- `logout` (`POST /logout`)
- `profile.index` (`GET /profile`)
- `favorites.index` (`GET /my-favorites`)
- `favorites.add` / `favorites.remove` (`POST|DELETE /favorites/{destinationId}`)
- `ratings.store` (`PUT /ratings/{destinationId}`)

### 4.2 Admin
- `admin.dashboard` (`GET /admin`)
- `admin.users.index` + `admin.users.status` + `admin.users.role`
- `admin.categories.index|store|update|delete`
- `admin.destinations.index|store|update|delete`
- `admin.stats.index`

## 5. Mapping route -> API backend

- `/` (landing + activity tabs `city-tour`, `food-tour`, `chill-bien`,
  `kham-pha-thien-nhien`, `van-hoa-lich-su`) ->
  `GET /api/v1/public/landing` +
  `GET /api/v1/public/activities/{slug}/recommendations?page=1&limit=3`
- `/destinations` -> `GET /api/v1/destinations` (popup detail ->
  `GET /api/v1/destinations/{id}`)
- `/my-favorites` -> `GET /api/v1/me/favorites`
- Admin dashboard -> `GET /api/v1/admin/stats/*`
