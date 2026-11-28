# Báo cáo cơ chế đề xuất — BE 1.3.0 (2026-11-28)

## Quyết định owner

- Rating là điểm tổng hợp từ nguồn chính thống (Google Maps / trang du lịch),
  **nhập tay qua admin bulk** — không dùng rating cá nhân của user.
- Thêm bảng `user_views` từ đầu; hồ sơ user suy từ **favorites + thói quen xem**.

## Đã triển khai (backend)

| Hạng mục | Chi tiết |
|---|---|
| Migration 0003 | `user_views` + `destinations.external_*` (đã lên compose DB: `f7a2c9d1e3b4`) |
| Worker insight | Ưu tiên external (`rating_source`, summary ghi nguồn) |
| Detail tracking | `GET /destinations/{id}` + Bearer → ghi `user_views` (best-effort) |
| `GET /me/recommendations` | matched ≥ 60 / explore 40–60 + diversity; user mới fallback hot |
| `GET /me/itinerary` | greedy khác-category liên tiếp + slot sáng/chiều/tối |
| Admin bulk | nhận `external_rating_avg/count/source` (create/update/bulk) |

## Verify

- Backend pytest: **26 passed** (22 cũ + 4 mới `test_recommendation.py`).
- Frontend phpunit: **14 passed** (không regression).
- Live qua gateway: user mới → matched 3 + explore 10 + itinerary 3 điểm xen
  category, kèm `reasons`/`components`; admin bulk external ok.
- Contract: `BE-API-1.3.0.md` + BOUNDARIES B11/B12.

## Chưa làm (theo quyết định "tính năng bỏ ngõ" + G3 HOLD)

- FE trang `/recommendations` (Ocean theme) — BE đã sẵn, chờ owner gọi.
- Ẩn form "Gửi đánh giá" → thay khối "Điểm tổng hợp ★ + nguồn".
- Worker `destination.viewed` event chưa mang `user_id` (hiện ghi trực tiếp từ router).

**G3 vẫn HOLD.**
