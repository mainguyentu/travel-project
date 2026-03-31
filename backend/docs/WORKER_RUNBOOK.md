# WORKER_RUNBOOK

Runbook vận hành cho `worker-service` (Kafka consumer, retry, DLQ).

## 1) Cơ chế reliability hiện tại

- Retry nội bộ theo config:
  - `WORKER_RETRY_MAX`
  - `WORKER_RETRY_BACKOFF_SECONDS`
- Nếu xử lý vẫn fail: event được publish sang `KAFKA_DLQ_TOPIC`.

## 2) Kiểm tra nhanh worker

1. Kiểm tra container:

```bash
docker compose ps worker-service
```

2. Theo dõi log:

```bash
docker compose logs -f worker-service
```

3. Dấu hiệu lỗi cần chú ý:

- `Worker event handling failed`
- `Worker unexpected error`
- `Worker loop error`

## 3) Replay event từ DLQ

Script:

```bash
python scripts/replay_dlq.py --limit 100
```

Tùy chọn:

- Dry run:

```bash
python scripts/replay_dlq.py --dry-run --limit 50
```

- Filter theo prefix event type:

```bash
python scripts/replay_dlq.py --event-prefix destination. --limit 100
```

Lưu ý:

- Script chỉ commit offset khi replay thành công.
- Nếu publish ngược lại topic đích thất bại, event không bị commit để tránh mất dữ liệu.

## 4) Quy trình xử lý sự cố DLQ tăng đột biến

1. Xác định event_type gây lỗi nhiều nhất (log + sample message).
2. Xác định nguyên nhân gốc (schema mismatch, dữ liệu bẩn, downstream unavailable).
3. Vá code/config tương ứng.
4. Chạy replay có kiểm soát theo lô nhỏ (`--limit 20` trước).
5. Theo dõi metric lỗi sau replay.
