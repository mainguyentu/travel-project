# Báo cáo UX/UI Public — Ocean theme + Dark Mode

Ngày: 2026-11-27 | Phạm vi: **public** (home/destinations/favorites/profile/auth)
| Trạng thái: **HOÀN THÀNH** | Admin: **chỉ thiết kế, chờ duyệt (§4)** |

## 1. Đã triển khai (public)

- **Hệ màu Ocean** (`frontend/public/css/app.css` viết lại, ~330 dòng):
  3 gradient cốt lõi + tokens Light/Dark + semantic theo đúng spec owner,
  chuyển theme qua `[data-theme]` + `localStorage` (có script chống nháy).
- **Header**: sticky + blur, logo gradient Ocean, nav desktop/mobile (768px),
  nút theme ◐, nút Đăng ký dạng CTA.
- **Home**: hero fullscreen overlay Ocean Signature + search nối API thật
  (`?q=` → Elasticsearch Pha B); Hoạt động (categories từ `public/landing`);
  Nổi bật / Rating cao (`.section-alt` Mist) / banner cao cấp (Ocean & Sand)
  / Được yêu thích.
- **Card**: ảnh `img_url` DB lazy-load, thiếu ảnh → placeholder Mist + chữ cái
  (không phủ gradient lên ảnh thật); badge ★; chip giá/views; nút Chi tiết
  (modal JS: ảnh trần + insight + metrics) + Yêu thích.
- **Destinations**: head + filter + empty-state + phân trang + nguồn search
  (Elasticsearch/DB); **auth** form-card; **favorites/profile**; **footer**
  4 cột (Deep Ocean / Deepest Navy).
- **Alert** có icon chữ (✓/⚠) + màu semantic theo theme.

## 2. Verification

| Check | Kết quả |
|---|---|
| 4 trang public qua gateway | 200 (home 18 cards/4 sections, destinations 15 cards, login/register form-card) |
| Toggle theme | có trong HTML, `localStorage` + chống FOUC |
| Frontend phpunit | 13 passed, 41 assertions |
| Backend pytest | 22 passed (không regression) |
| SLO + smoke | 5/5 + 5/5 |

## 3. Ghi chú

- `resources/css/app.css` (Vite) vẫn để trống — CSS public build tay ở
  `public/css/app.css`; dọn Vite khi làm admin hoặc khi owner quyết.
- Guidelines đã cập nhật: `figma-design/guidelines/Guidelines.md`
  (hệ màu, nguyên tắc, quy ước public/admin).

## 4. Thiết kế UX/UI Admin — CHỜ DUYỆT (chưa code)

### 4.1 Mục tiêu & phạm vi

Áp Ocean theme + dark mode cho 6 trang admin hiện có
(dashboard, users, categories, destinations, stats, audit-logs),
giữ nguyên mọi luồng nghiệp vụ (filter from/to, bulk JSON, PATCH
status/role, audit). Responsive: sidebar → topbar trượt dưới 900px.

### 4.2 Layout đề xuất

- Giữ `layouts/admin` (sidebar + topbar), đổi sang tokens Ocean:
  sidebar Light = trắng + active-item gradient Ocean (chữ trắng);
  Dark = `#122536` + active giữ gradient.
- Topbar: brand nhỏ + nút theme ◐ (dùng chung `toggleTheme`) + link
  "Xem site" + email admin + Đăng xuất.
- Content: `.container` + page-head (tiêu đề + mô tả + action chính bên phải).

### 4.3 Từng trang

| Trang | Thiết kế đề xuất |
|---|---|
| Dashboard | 4 thẻ KPI (tổng destinations/users/favorites/ratings — lấy từ API có sẵn khi mở rộng, trước mắt tính từ top-lists) + 3 panels Top yêu thích/rating/views dạng bảng gọn + filter from/to kiểu `.filters` public |
| Users | Bảng Ocean (header Surface Muted, viền token): badge role (admin = chip cát, user = chip mist), badge status (active = success, locked = error + icon 🔒/✓); PATCH giữ form inline, nút Lưu nhỏ |
| Categories | Form tạo kiểu `.form-card` ngang (name/slug/desc + CTA); bảng + nút Sửa/Xóa ghost; xóa có `confirm()` |
| Destinations | Toolbar: filter status/keyword + nút "Thêm" mở form; bulk JSON vào `<details>` styled; bảng thêm cột rating/views + thumb 48px (img_url hoặc placeholder Mist); nút Xóa `confirm()` |
| Stats | Gộp vào dashboard (route `/stats` render cùng view, bỏ `stats.blade` include lặp); thêm chú thích nguồn ES/DB |
| Audit logs | Bảng + filter action/entity; cột detail JSON rút gọn `<details>`; badge action màu semantic (create=success, update=info, delete=error, bulk_create=warning) |

### 4.4 Không đổi

- Routes, controller logic, API calls, response shape; chỉ Blade + CSS
  (thêm classes `.admin-*` dùng tokens, không đụng classes public dùng chung
  trừ khi cần và đã sửa mọi view).
- Không thêm chart lib; KPI = số + delta text (đủ cho vận hành).

### 4.5 Dự kiến verify sau duyệt

Rebuild frontend → 6 trang admin 200 (session admin) → phpunit →
thêm test `admin_dashboard_renders` nếu thiếu → cập nhật Guidelines §3.

---
**Owner duyệt §4 (hoặc góp ý) thì tôi mới code admin.**
