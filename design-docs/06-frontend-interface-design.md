# 06 - Frontend Interface Design (Laravel Blade)

## 1. Cấu trúc frontend view đề xuất

```text
frontend/
  resources/
    views/
      layouts/
      components/
      pages/
    css/
    js/
```

## 2. Layout và component chuẩn

### 2.1 Layout public
- `layouts/public.blade.php`
  - Header
  - Main content slot
  - Footer

### 2.2 Layout admin
- `layouts/admin.blade.php`
  - Sidebar
  - Topbar
  - Main content slot

### 2.3 Shared components
- Navbar
- Footer
- Destination card
- Rating stars
- Empty state
- Pagination
- Filter panel
- Alert/Toast

## 3. Public page blueprint

### 3.1 Landing
- Hero section (banner + CTA)
- Featured destinations
- Popular categories
- Why Alats Travel section

### 3.2 Destination list
- Filter bar: category, price level, rating
- Grid card destination
- Pagination

### 3.3 Destination detail
- Gallery/banner ảnh
- Thông tin chính: name, rating_avg, price_level, địa chỉ
- Mô tả + insight (`final_data`)
- Nút favorite
- Form rating
- Nearby places

## 4. Admin page blueprint

### 4.1 Dashboard
- KPI cards
- Top favorite table
- Top rating table
- Top views table

### 4.2 Category management
- List + create/edit modal hoặc trang riêng

### 4.3 Destination management
- List + form create/update
- Mapping category

### 4.4 User management
- List user
- Action lock/unlock
- Action đổi role

## 5. Frontend state và API integration

- Controller gọi API lấy data và xử lý rồi truyền qua view.
- Lưu access token an toàn phía client theo chiến lược đã chốt.
- Route quản lý, phân phối điều hướng của trang web.

## 6. Styling guideline

- CSS tách file theo layer:
  - `base.css`
  - `components.css`
  - `pages.css`
- Không viết inline style trong Blade.
