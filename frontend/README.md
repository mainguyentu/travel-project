# Frontend

Thư mục frontend hiện ở trạng thái khởi tạo và chưa có scaffold chính thức.

## Mục tiêu

Frontend sẽ tiêu thụ API từ backend thông qua API Gateway:
- Base URL local: `http://localhost:8080`
- API base path: `/api/v1`

## Trạng thái hiện tại

- Chưa có framework/runtime được cấu hình trong thư mục này.
- Chưa có scripts build/run/test riêng cho frontend.

## Hợp đồng tích hợp backend (dự kiến)

Các nhóm endpoint chính cần dùng:
- Auth: `/api/v1/auth/*`
- Public khám phá điểm đến: `/api/v1/public/*`
- Destination chi tiết: `/api/v1/destinations/*`
- User interaction: `/api/v1/me/*`
- Admin: `/api/v1/admin/*`

Tham khảo chi tiết API tại:
- `../design-docs/02-api-design.md`
- `../backend/README.md`

## Đề xuất bước tiếp theo

1. Chọn stack frontend (ví dụ: React + Vite hoặc Next.js).
2. Tạo scaffold project + scripts (`dev`, `build`, `test`, `lint`).
3. Thiết lập env (`VITE_API_BASE_URL` hoặc tương đương).
4. Cập nhật README này theo stack thực tế và quy trình chạy.

## Lưu ý

- Không hardcode secret trong mã frontend.
- CORS backend hiện cho phép cấu hình qua `CORS_ORIGINS` ở backend.