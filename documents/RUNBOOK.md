# Runbook vận hành (Pha C) — Travel Project

## 1. Dịch vụ (7 services)

`docker compose ps` phải thấy Up: postgres (healthy), redis (healthy),
elasticsearch (healthy), backend, frontend, api-gateway (`:8080`), worker.

## 2. Kiểm tra nhanh

```powershell
python scripts/smoke_p3.py                       # 5/5: gateway, health, landing, home, login
curl.exe -s http://127.0.0.1:8080/metrics        # travel_uptime_seconds, rate limits
curl.exe -s http://127.0.0.1:8080/ready          # {"ready":true,"checks":{...}}
curl.exe -s http://127.0.0.1:8080/gateway-health
```

## 3. Rate limit (IP 120/phút, user 60/phút — owner đã chốt giữ)

- 2 lớp: nginx gateway (`limit_req 120r/m`, burst 20) + backend middleware
  (IP 120/phút, user-key 60/phút sau khi xác thực).
- Vượt ngưỡng → `429 {success:false, error:{code:RATE_LIMITED}, meta:{retry_after}}`
  + header `Retry-After`. In-memory sliding window, reset khi restart backend.
- `/health` và `/api/v1/health` được miễn.
- Scale-out: đổi sang Redis-backed counter (ghi chú — hiện single-replica).

## 4. Sự cố thường gặp

| Triệu chứng | Kiểm tra | Khắc phục |
|---|---|---|
| `search_engine=db` thay vì elasticsearch | `docker compose ps elasticsearch`, `worker logs` | `docker compose up -d elasticsearch worker`, rồi `python scripts/reindex.py` trong backend |
| Worker không enrich insight | `redis-cli XLEN travel-events`, `docker compose logs worker` | restart worker; chạy `scripts/worker.py --once` để vét |
| 500 frontend Blade | `docker compose logs frontend`, owner `storage/` | rebuild frontend (Dockerfile đã chown www-data) |
| 401 internal | header `X-Internal-Key` | set `INTERNAL_API_KEY` khớp backend env |
| ES đỏ/no disk | `/_cluster/health` | single-node dev: xóa volume `esdata` + reindex (mất index, DB vẫn nguyên) |

## 5. Backup/restore (U6 — RESOLVED 2026-11-27: RPO 24h, retention 7 bản, on-call: project owner)

- Script: `sh scripts/backup.sh` (giữ tối đa 7 bản trong `./backups/`).
- Lịch gợi ý (cron host): `0 2 * * * cd /path/travel-project && sh scripts/backup.sh`.
- Khôi phục: `docker compose exec -T postgres psql -U postgres travel < backups/travel-YYYYMMDD-HHMMSS.sql`.
- Thủ công 1 lần: `docker compose exec postgres pg_dump -U postgres travel > backup.sql`.
- ES: reindex lại từ DB (`scripts/reindex.py`) — không backup index.
- Redis streams: không persistent quan trọng (events tái tạo từ request mới).

## 5b. Checklist deploy production (U1-F2/F3/G2 — bắt buộc trước khi gỡ G3 HOLD)

- [ ] TLS termination ở gateway/LB (dev HTTP chỉ hợp lệ local).
- [ ] `JWT_SECRET` + `INTERNAL_API_KEY` mạnh qua env (không dùng default compose).
- [ ] Frontend: `SESSION_SECURE_COOKIE=true` (khi đã có HTTPS), `APP_DEBUG=false`.
- [ ] `JWT_SECRET` ≥ 32 ký tự ngẫu nhiên; xoay khi lộ.
- [ ] Cron backup U6 đã bật + kiểm tra khôi phục 1 lần.
- [ ] Rate-limit giữ 120 IP / 60 user (đã chốt Pha C) trừ khi đo tải mới.

## 6. Triển khai phiên bản mới

```powershell
docker compose build backend frontend worker api-gateway
docker compose up -d
python scripts/smoke_p3.py
```

Rollback: `docker compose down` (images cũ còn tag `latest` local); DB volume
`pgdata` giữ nguyên nên không mất dữ liệu.
