# 05 - UX/UI Guidelines

## 1. Mục tiêu trải nghiệm

- Truy cập thông tin điểm đến nhanh, trực quan.
- Tạo cảm giác tươi mát, hiện đại của thành phố biển.
- Hỗ trợ thao tác quản trị rõ ràng, tối ưu hiệu suất công việc admin.

## 2. Nguyên tắc thiết kế tổng quát

- Ưu tiên tính rõ ràng hơn hiệu ứng.
- Component tái sử dụng, nhất quán spacing và typography.
- Không lạm dụng bo góc lớn; radius vừa phải.
- Tách CSS/JS riêng, không inline style/script.

## 3. Màu sắc và thị giác

- Dùng palette tông biển: xanh dương, xanh ngọc, trắng, xám trung tính.
- Gradient nhẹ cho hero/section title, tránh quá chói.
- Duy trì contrast đảm bảo readability.

## 4. Typography

- Heading rõ ràng theo cấp bậc H1/H2/H3.
- Body text dễ đọc, line-height thoáng.
- Tránh dùng quá nhiều font; tối đa 2 font family.

## 5. UX cho public frontend

- Landing: hero + CTA + section điểm đến nổi bật.
- Danh sách: filter panel dễ thao tác, phản hồi tức thì.
- Chi tiết: thông tin quan trọng nằm “above the fold” (tên, ảnh, rating, giá, map).
- Favorite/rating có feedback trạng thái rõ ràng.

## 6. UX cho admin dashboard

- Sidebar navigation cố định, route rõ ràng theo domain.
- Bảng dữ liệu hỗ trợ sort/search/pagination.
- Form CRUD có validation message cụ thể.
- Dashboard stats dùng card + bảng top ranking.

## 7. Accessibility cơ bản

- Semantic HTML đúng chuẩn.
- Label cho input và button có text rõ nghĩa.
- Focus state rõ ràng.
- Alt text cho ảnh quan trọng.

## 8. Responsive guideline

- Breakpoint tối thiểu:
  - Mobile: < 768
  - Tablet: 768 - 1023
  - Desktop: >= 1024
- Filter list có thể chuyển từ sidebar sang drawer trên mobile.
