# U3 — Viewports + Performance targets (owner decision 2026-11-27)

## Viewports (FSTD-003-R001)

| Thiết bị | Breakpoint | Cover bởi CSS hiện tại |
|---|---|---|
| Mobile | 360px | `@media 768px` (stack, hero, grid 1 col) |
| Tablet | 768px | chính breakpoint 768px |
| Admin sidebar | 900px | `@media 900px` (sidebar ngang) |
| Desktop | 1280px | layout mặc định (container 1200px) |

Layout dùng `layouts/public` + `layouts/admin` đều có
`<meta name="viewport" content="width=device-width, initial-scale=1.0">`.
Quy tắc: mọi trang mới phải render đúng ở 360/768/1280 trước khi merge.

## Performance targets (FSTD-007-R001)

Đo server-side qua gateway (LAN, 2026-11-27):

| Trang | TTFB/server | HTML size | Ghi chú |
|---|---|---|---|
| `/` (home) | ~0.18s | ~18 KB | có cache API 5' (`API_CACHE_ENABLED`) |
| `/destinations` | ~0.06s | ~15 KB | |

Targets (lab, áp dụng khi đo Lighthouse trên stack thật):

| Metric | Target | Ghi chú |
|---|---|---|
| LCP | ≤ 2.5s | ảnh DB/thumb 48px + loading lazy đã có |
| INP | ≤ 200ms | Blade SSR, JS chỉ theme-toggle/modal |
| CLS | ≤ 0.1 | ảnh có width/height hoặc aspect-box (backlog: thêm `aspect-ratio` cho thumb) |

- Cách đo lab: Lighthouse CI (backlog — chưa có workflow; chạy thủ công
  `lighthouse http://127.0.0.1:8080/ --view` khi cần).
- RUM production: bỏ ngõ (chưa có endpoint thu thập).
