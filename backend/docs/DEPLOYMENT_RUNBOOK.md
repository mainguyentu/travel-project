# DEPLOYMENT_RUNBOOK

Runbook cho CI/CD deploy staging và production qua GitHub Actions.

## 1) Workflow map

- Build + push image: `.github/workflows/release-build.yml`
- Deploy staging + smoke/SLO check: `.github/workflows/deploy-staging.yml`
- Deploy production + approval + rollback + SLO check: `.github/workflows/deploy-production.yml`
- Release notes draft automation: `.github/workflows/release-notes.yml`
- Reusable post-deploy SLO checks: `.github/workflows/post-deploy-slo-check.yml`

## 2) Artifact và image tags

Release build đẩy 2 images lên GHCR:

- `ghcr.io/<owner>/<repo>/backend:<tag>`
- `ghcr.io/<owner>/<repo>/api-gateway:<tag>`

Tag mặc định là `GITHUB_SHA`.

## 3) Môi trường đích

Remote host chạy bằng `docker-compose.deploy.yml` và cần có file `.env` chứa secret/runtime config.

Lệnh deploy chính:

```bash
docker compose -f docker-compose.deploy.yml pull
docker compose -f docker-compose.deploy.yml up -d --remove-orphans
```

## 4) Required GitHub secrets

### Shared

- `GHCR_USERNAME`
- `GHCR_TOKEN` (PAT có quyền `read:packages`)

### Staging

- `STAGING_SSH_HOST`
- `STAGING_SSH_USER`
- `STAGING_SSH_KEY`
- `STAGING_SSH_PORT` (optional, default 22)
- `STAGING_DEPLOY_PATH` (folder chứa `docker-compose.deploy.yml`)
- `STAGING_BASE_URL` (dùng cho post-deploy SLO checks)

### Production

- `PROD_SSH_HOST`
- `PROD_SSH_USER`
- `PROD_SSH_KEY`
- `PROD_SSH_PORT` (optional, default 22)
- `PROD_DEPLOY_PATH`
- `PROD_BASE_URL`

## 5) Approval gates

- Job production dùng environment `production`.
- Cần cấu hình required reviewers trong GitHub Environments để bắt buộc approval trước khi chạy deploy.
- Auto deploy production chỉ chạy khi commit message chứa `[deploy]`.
- Manual dispatch bắt buộc `confirm_phrase=DEPLOY_PRODUCTION`.

## 6) Rollback procedure

Rollback được thực hiện bằng workflow dispatch `Deploy Production` với input:

- `image_tag`: giữ nguyên hoặc bất kỳ
- `rollback_to_tag`: điền tag stable cần quay lại

Workflow sẽ ưu tiên `rollback_to_tag` và redeploy toàn bộ services bằng image đó.

## 7) Post-deploy SLO check

Workflow `post-deploy-slo-check.yml` kiểm tra:

- `/health` (mặc định < 300ms)
- `/api/v1/destinations?page=1&limit=5` (mặc định < 500ms)
- `/api/v1/analytics/summary` (mặc định < 800ms)

Kết quả được lưu thành artifact `slo-report-<env>-<run_id>`.

## 8) Failure handling

1. Nếu deploy fail trước bước `up -d`: kiểm tra credential GHCR/SSH và network.
2. Nếu deploy pass nhưng SLO fail:
   - Kiểm tra logs gateway/backend/worker.
   - Nếu lỗi nghiêm trọng: rollback ngay qua production workflow với `rollback_to_tag`.
3. Ghi nhận incident theo `SECURITY_RUNBOOK.md` và `OBSERVABILITY_BASELINE.md`.

## 9) Staging Rollout Checklist (Destination Image -> Cloudinary)

Checklist này dùng cho rollout tính năng migrate destination images lên Cloudinary trên staging.

### 9.1 Pre-deploy checks

- [ ] Cloudinary credential đã đủ trên staging `.env`:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
   - `CLOUDINARY_UPLOAD_FOLDER`
- [ ] Flag ban đầu để `DESTINATION_IMAGE_CLOUDINARY_ENABLED=false`.
- [ ] Deploy env có đầy đủ tham số timeout/limit:
   - `DESTINATION_IMAGE_TIMEOUT_SECONDS`
   - `DESTINATION_IMAGE_MAX_BYTES`
   - `DESTINATION_IMAGE_UPLOAD_CONCURRENCY`
   - `DESTINATION_IMAGE_BACKFILL_BATCH_SIZE`
   - `DESTINATION_IMAGE_BACKFILL_SLEEP_SECONDS`
   - `DESTINATION_IMAGE_BACKFILL_CHECKPOINT_FILE`
- [ ] Đảm bảo path checkpoint writable trong container (`./.runtime/...` mặc định).

### 9.2 Deploy và smoke khi flag OFF

- [ ] Trigger workflow staging deploy với image tag cần rollout.
- [ ] Xác minh compose đã lên đủ service: `auth-service`, `destination-service`, `interaction-service`, `admin-service`, `analytics-service`, `worker-service`, `api-gateway`.
- [ ] Chạy post-deploy SLO check và xác minh pass:
   - `/health`
   - `/api/v1/destinations?page=1&limit=5`
   - `/api/v1/analytics/summary`

### 9.3 Bật online migration (flag ON)

- [ ] Set `DESTINATION_IMAGE_CLOUDINARY_ENABLED=true` trên staging và restart backend services.
- [ ] Test `POST /api/v1/admin/destinations` với URL ảnh không phải Cloudinary.
- [ ] Xác minh response/DB:
   - `img_urls` là URL Cloudinary (hoặc fallback URL gốc nếu lỗi per-url)
   - `img_url` = phần tử đầu tiên của `img_urls`
- [ ] Test `POST /api/v1/admin/destinations/bulk` và `PUT /api/v1/admin/destinations/{id}` theo cùng rule.
- [ ] Kiểm tra log có field theo thiết kế khi fallback: `destination_id`, `source_url`, `reason`, `stage`.

### 9.4 Canary backfill trên staging

- [ ] Chạy dry backfill nhỏ để kiểm tra luồng:

```bash
python scripts/backfill_destination_images.py --batch-size 50 --max-batches 2
```

- [ ] Xác minh file checkpoint được tạo/cập nhật.
- [ ] Xác minh log tổng kết batch có các chỉ số: `processed`, `migrated`, `skipped`, `fallback`.
- [ ] Chạy lại cùng checkpoint để xác minh idempotent/resume không migrate trùng.

### 9.5 Exit criteria cho staging

- [ ] SLO sau deploy và sau backfill vẫn trong ngưỡng.
- [ ] Không có error rate bất thường trên worker/gateway/backend logs.
- [ ] Dữ liệu destination mới tạo/sửa trên staging đã tuân thủ rule Cloudinary/fallback.
- [ ] Có bằng chứng (artifact + log + checkpoint) để sign-off trước production rollout.
