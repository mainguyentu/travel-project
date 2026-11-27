# 11 - Coding Conventions

## 1. Nguyên tắc chung

- Ưu tiên code rõ ràng, dễ bảo trì.
- Tách layer: controller/router -> service -> repository.
- Không trộn business logic vào route handler.

## 2. Backend (FastAPI/Python)

- Dùng type hints đầy đủ.
- Pydantic schema cho request/response.
- Tên biến/function theo `snake_case`.
- Class theo `PascalCase`.
- Mỗi domain có module riêng.

## 3. API conventions

- Path dùng `kebab-case` hoặc plural resource nhất quán.
- Dùng danh từ cho endpoint, động từ qua HTTP method.
- Trả lỗi theo error envelope thống nhất.

## 4. Database conventions

- Bảng và cột dùng `snake_case`.
- Timestamp chuẩn: `created_at`, `updated_at`.
- Foreign key đặt tên theo `{entity}_id`.

## 5. Frontend (Laravel Blade + JS)

- Tách view component tái sử dụng.
- Không viết inline CSS/JS.
- JS module theo domain API.
- Đặt tên file view theo cấu trúc route.

## 6. Git conventions

- Branch: `feature/*`, `fix/*`, `chore/*`
- Commit message rõ ràng, theo conventional commit nếu có.
- PR cần mô tả scope + checklist test.

## 7. Documentation conventions

- Mỗi thay đổi lớn về API/DB phải cập nhật tài liệu liên quan.
- Giữ thuật ngữ nhất quán: destination, category, favorite, rating.
