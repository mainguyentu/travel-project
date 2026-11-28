# Frontend Contract — v1.2.0 (Recommendations + rating-summary + nút tim)

Scope: giữ nguyên FE 1.1.0 + trang gợi ý + khối điểm tổng hợp + nút tim đè ảnh.
FSTD-004-R001/R003, FSTD-005-R001, XSTD-001-R005.

## 1. Routes mới

| Method | URI | Controller | Guard | Backend call |
|--------|-----|-----------|-------|--------------|
| GET | `/recommendations` | RecommendationController@index | `session.auth` | `me/recommendations?limit` + `me/itinerary?limit` (param `days`) |

## 2. Views mới / sửa

- `recommendations/index.blade.php`: 3 sections — Phù hợp (matched + reasons + % khớp),
  Có thể thích (explore), Lịch trình gợi ý (order + slot buổi + % hợp) + form chọn 3/5/7 điểm.
- `components/rating-summary.blade.php` (mới): `★ avg (count đánh giá · nguồn)` —
  external (`google_maps` → "Google Maps") hoặc internal; cảnh báo "Ít dữ liệu" khi
  insight chưa `ok`. Dùng ở `favorites.blade.php` thay `rating-form`.
- `destination-detail-modal` (JS `app.js`): render khối điểm tổng hợp ★ + nguồn
  thay dòng "Rating: X" (không còn form chấm điểm cá nhân trong modal).
- `components/destination-card.blade.php`: nút ♥ dạng icon tròn `.fav-heart`
  đè góc trái-trên ảnh (`.fav-overlay`), badge rating giữ góc phải; bỏ nút
  "♥ Yêu thích" trong card-actions (chỉ còn "Xem chi tiết").
- `components/navbar.blade.php`: thêm link "Gợi ý" (desktop + mobile, khi đã login).
- Route `PUT /ratings/{id}` + `rating-form` giữ nguyên (không xóa) nhưng không còn
  render ở trang nào — BE `PUT /me/ratings/*` không tham gia tính match (BE 1.3.0).

## 3. Không đổi

Routes/views/state/identity như FE 1.1.0 (session tokens, ApiClient cache +
refresh-and-retry, `session.auth`/`session.admin` guards).

## Change history

- 1.2.0 (2026-11-28): recommendations + rating-summary + fav-heart.
  Verify: phpunit 15 passed/58 assertions (mới `test_recommendations_page_renders_matched_explore_itinerary`).
