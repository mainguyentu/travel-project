# OBSERVABILITY_BASELINE

Baseline theo dõi DB/Redis/API/Worker cho staging và production.

## 1) Database guardrails

Config hiện có:

- `DB_POOL_SIZE`
- `DB_MAX_OVERFLOW`
- `DB_POOL_TIMEOUT`
- `DB_POOL_RECYCLE`

Threshold cảnh báo khuyến nghị:

- P95 API latency > 800ms trong 10 phút.
- Tỷ lệ lỗi 5xx > 2% trong 5 phút.
- Connection timeout tăng bất thường (`QueuePool limit`/`timeout`).
- Migration runtime vượt baseline > 2x.

## 2) Redis guardrails

Config hiện có:

- `REDIS_MAX_CONNECTIONS`
- `REDIS_SOCKET_CONNECT_TIMEOUT`
- `REDIS_SOCKET_TIMEOUT`

Threshold cảnh báo khuyến nghị:

- Cache error log (`Redis get/set failed`) > 20 lần/5 phút.
- Redis memory usage > 80%.
- Redis CPU > 75% liên tục 10 phút.
- Network timeout tới Redis tăng đột biến.

## 3) Log/Trace baseline

- Mọi response phải có `X-Request-Id`.
- Log cần include `request_id` để correlate gateway và app logs.
- Action auth/admin phải có bản ghi trong `audit_logs`.

## 4) SLO baseline (đang áp dụng)

- API availability: 99.5%/tháng.
- P95 read endpoints: < 500ms.
- P95 write endpoints: < 800ms.
- Worker DLQ rate: < 0.5% tổng events/giờ.

Đối soát sau deploy:

- Workflow `.github/workflows/post-deploy-slo-check.yml` chạy tự động sau staging/prod deploy.
- Endpoint kiểm tra:
   - `/health`
   - `/api/v1/destinations?page=1&limit=5`
   - `/api/v1/analytics/summary`

## 5) Quy trình khi vượt ngưỡng

1. Xác nhận alert không phải false positive.
2. Khoanh vùng thành phần (gateway/app/db/redis/worker).
3. Áp dụng mitigation:
   - Scale service
   - Tăng pool hợp lý
   - Giảm traffic qua rate-limit tạm thời
4. Theo dõi metric hồi phục 15-30 phút.
5. Ghi nhận RCA + hành động phòng ngừa.

## 6) Activity Recommendation telemetry (Task 11)

Endpoint:

- `GET /api/v1/public/activities/{activity_slug}/recommendations`

Log event JSON:

- `event = activity_recommendation.telemetry`
- Nhãn chính: `activity_slug`, `request_id`, `page`, `limit`, `budget_level`
- Signal chính:
   - `latency_ms`
   - `fallback_used` (true/false)
   - `empty_result` (true/false)
   - `endpoint_error_code`
   - `counts.highlight`, `counts.recommended`, `counts.trending`

Gợi ý query dashboard (theo log backend):

- Latency p95 theo activity:
   - lọc `event=activity_recommendation.telemetry`
   - group by `activity_slug`
   - tính p95(`latency_ms`)
- Fallback rate:
   - tỉ lệ bản ghi `fallback_used=true` trên tổng bản ghi cùng khoảng thời gian
- Empty-result rate:
   - tỉ lệ bản ghi `empty_result=true` trên tổng bản ghi cùng khoảng thời gian
