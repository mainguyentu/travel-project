# Backend API Contract — v1.3.0 (Recommendation + itinerary từ insight)

Scope: giữ nguyên BE 1.2.0 + cơ chế đề xuất đọc từ `destination_insights.final_data`.
Rating là điểm tổng hợp từ nguồn chính thống (nhập tay qua admin bulk),
KHÔNG dùng rating cá nhân của user. Hồ sơ user suy từ favorites + user_views.
XSTD-001-R002; BSTD-004-R001/R002/R004/R007/R009.

## 1. Không đổi envelope/guards

Envelope, `expires_in` phút, `require_admin`, `X-Internal-Key` như 1.2.0.

## 2. Mới so với 1.2.0

### 2.1 DB migration 0003 (`f7a2c9d1e3b4`)

- `user_views(user_id, destination_id, view_count, last_viewed_at)` — PK kép,
  FK cascade; ghi từ `GET /destinations/{id}` khi có Bearer token (best-effort,
  không block response).
- `destinations.external_rating_avg (0..5)`, `external_rating_count`,
  `external_source` (default `manual`) — nhập tay qua admin create/update/bulk.

### 2.2 Insight (worker `build_insight`)

- Nếu `external_rating_count > 0`: `rating_avg/count/sum` trong `final_data`
  lấy từ external + `rating_source = external_source`; summary ghi nguồn.
- Ngược lại giữ hành vi 1.2.0 (`rating_source = "internal"`).

### 2.3 `GET /me/recommendations?limit=` (auth required)

- Profile user: `top_categories` (favorite ×1.0, xem lại ≥2 lần ×0.6, xem 1 lần ×0.4,
  chuẩn hóa max),
  `preferred_price` (mode price_level), `is_new` (chưa có tín hiệu).
- Match 0..100 = category (0..45) + quality blended (0..35, trần 15 nếu
  insight `insufficient_data`) + popularity (0..10) + price (0..10).
- `matched`: `match ≥ 60`, trừ des đã ♥; user mới → fallback hot toàn site.
- `explore`: `40 ≤ match < 60` hoặc category hoàn toàn mới (≥ 30) — tối đa 10,
  mỗi category ≤ 2 (diversity).
- Response: `{matched: [{destination, match, reasons, components}], explore: [...],
  profile: {top_categories, preferred_price, is_new}}`.

### 2.4 `GET /me/itinerary?limit=5` (auth required, max 10)

- Pool từ `matched` (fallback `explore`); greedy: des đầu = match cao nhất,
  các des sau ưu tiên khác category des trước.
- Mỗi item: `{order, destination, match, reasons, slot}` — slot sáng/sáng/chiều/chiều/tối.
- Response: `{itinerary: [...], total_match, profile}`.

## 3. Không đổi

Bulk/analytics/internal/activities/audit/search/events như 1.2.0.
`PUT /me/ratings/*` giữ nguyên (không tham gia tính match).

## Change history

- 1.3.0 (2026-11-28): recommendation + itinerary từ insight; user_views;
  external rating nhập tay qua bulk; worker ưu tiên external.
  Tests: `test_recommendation.py` 4 passed.
