# 03 - Database Design (PostgreSQL)

## 1. Mục tiêu dữ liệu

- Mô hình dữ liệu quan hệ rõ ràng, đảm bảo toàn vẹn.
- Tối ưu truy vấn danh sách địa điểm, favorite, rating.
- Hỗ trợ mở rộng analytics theo event-driven.

## 2. Danh sách bảng chính

1. `users`
2. `user_tokens`
3. `categories`
4. `category_destinations`
5. `destinations`
6. `destination_insights`
7. `favorites`
8. `ratings`
9. `activities` (mới — theo code hiện tại, phục vụ activity recommendation)
10. `destination_activities` (mới — mapping destination ↔ activity)
11. `activity_rules` (mới — trọng số scoring theo activity)
12. `destination_features` (mới — đặc trưng destination cho scoring)
13. `destination_metrics` (mới — bộ đếm tổng hợp favorite/rating/view)
14. `audit_logs` (mới — theo code hiện tại, log hành động auth/admin)

## 3. Schema chi tiết (MVP)

### 3.1 `users`
- `id` BIGSERIAL PK
- `name` VARCHAR(120) NOT NULL
- `email` VARCHAR(255) UNIQUE NOT NULL
- `password_hash` TEXT NOT NULL
- `role` VARCHAR(20) NOT NULL DEFAULT `user` (`user|admin`)
- `status` VARCHAR(20) NOT NULL DEFAULT `active` (`active|locked`)
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### 3.2 `user_tokens`
- `id` BIGSERIAL PK
- `user_id` BIGINT NOT NULL REFERENCES `users(id)`
- `token_access` TEXT NOT NULL
- `refresh_token` TEXT NOT NULL
- `revoked_at` TIMESTAMPTZ NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### 3.3 `categories`
- `id` BIGSERIAL PK
- `name` VARCHAR(120) NOT NULL
- `slug` VARCHAR(160) UNIQUE NOT NULL
- `descriptions` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### 3.4 `destinations`
- `id` BIGSERIAL PK
- `place_id` VARCHAR(120) NULL, indexed (mới — theo code hiện tại)
- `name` VARCHAR(180) NOT NULL
- `slug` VARCHAR(220) UNIQUE NOT NULL
- `address` TEXT NULL
- `description` TEXT NULL
- `rating_avg` NUMERIC(3,2) NOT NULL DEFAULT 0
- `rating_count` BIGINT NOT NULL DEFAULT 0 (mới — theo code hiện tại)
- `lat` NUMERIC(10,7) NULL
- `lng` NUMERIC(10,7) NULL
- `price_level` VARCHAR(20) NOT NULL DEFAULT `medium`
- `price_raw_text` TEXT NULL (mới — giữ text gốc khi bulk import)
- `open_hour` VARCHAR(120) NULL
- `open_hours_raw_text` VARCHAR(200) NULL (mới — theo code hiện tại)
- `open_hour_open` VARCHAR(120) NULL (mới — theo code hiện tại)
- `open_hour_close` VARCHAR(120) NULL (mới — theo code hiện tại)
- `img_url` TEXT NULL
- `img_urls` JSON NULL (mới — nhiều ảnh, migrate Cloudinary)
- `url_map` TEXT NULL
- `view_count` BIGINT NOT NULL DEFAULT 0
- `status` VARCHAR(20) NOT NULL DEFAULT `active`
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### 3.5 `category_destinations`
- `category_id` BIGINT NOT NULL REFERENCES `categories(id)`
- `destination_id` BIGINT NOT NULL REFERENCES `destinations(id)`
- PK composite: (`category_id`, `destination_id`)

### 3.6 `destination_insights`
- `destination_id` BIGINT PK REFERENCES `destinations(id)`
- `human_override` JSONB NULL
- `score_snapshot` JSONB NULL
- `final_data` JSONB NOT NULL
- `insight_cache` JSONB NULL (cache tổng hợp để cập nhật O(1))
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

### 3.7 `favorites`
- `user_id` BIGINT NOT NULL REFERENCES `users(id)`
- `destination_id` BIGINT NOT NULL REFERENCES `destinations(id)`
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
- `deleted_at` TIMESTAMPTZ NULL
- PK composite: (`user_id`, `destination_id`)

### 3.8 `ratings`
- `user_id` BIGINT NOT NULL REFERENCES `users(id)`
- `destination_id` BIGINT NOT NULL REFERENCES `destinations(id)`
- `rating_score` SMALLINT NOT NULL CHECK (`rating_score BETWEEN 1 AND 5`)
- `comment` TEXT NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
- `updated_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()
- PK composite: (`user_id`, `destination_id`)

### 3.9 `activities` (mới — theo code hiện tại)
- `id` BIGSERIAL PK
- `name` VARCHAR(120) NOT NULL
- `slug` VARCHAR(160) UNIQUE NOT NULL, indexed
- `description` TEXT NULL
- `is_active` BOOLEAN NOT NULL DEFAULT TRUE
- `created_at`, `updated_at` TIMESTAMPTZ

### 3.10 `destination_activities` (mới — theo code hiện tại)
- `destination_id` BIGINT NOT NULL REFERENCES `destinations(id)`
- `activity_id` BIGINT NOT NULL REFERENCES `activities(id)`
- `weight` NUMERIC(4,3) NOT NULL DEFAULT 1.0
- `source` VARCHAR(20) NOT NULL DEFAULT `manual`
- `created_at`, `updated_at` TIMESTAMPTZ
- PK composite: (`destination_id`, `activity_id`)

### 3.11 `activity_rules` (mới — theo code hiện tại)
- `activity_id` BIGINT PK REFERENCES `activities(id)`
- `scenery_weight`, `accessibility_weight`, `crowd_weight`, `value_weight`
  NUMERIC(5,4) NOT NULL DEFAULT 0.25
- `crowd_mode` VARCHAR(20) NOT NULL DEFAULT `prefer_low`
- `min_match_threshold` NUMERIC(4,3) NOT NULL DEFAULT 0
- `created_at`, `updated_at` TIMESTAMPTZ

### 3.12 `destination_features` (mới — theo code hiện tại)
- `destination_id` BIGINT PK REFERENCES `destinations(id)`
- `is_indoor`, `is_outdoor` BOOLEAN NULL
- `suitable_time` VARCHAR(20) NOT NULL DEFAULT `both`
- `budget_level` VARCHAR(20) NULL
- `duration_suggested_minutes` INTEGER NULL
- `created_at`, `updated_at` TIMESTAMPTZ

### 3.13 `destination_metrics` (mới — theo code hiện tại)
- `destination_id` BIGINT PK REFERENCES `destinations(id)`
- `favorite_count`, `rating_count`, `rating_sum`, `view_count` BIGINT NOT NULL DEFAULT 0
- `updated_at` TIMESTAMPTZ

### 3.14 `audit_logs` (mới — theo code hiện tại)
- `id` BIGSERIAL PK
- `actor_user_id` BIGINT NULL REFERENCES `users(id)`, indexed
- `actor_email` VARCHAR(255) NULL, `actor_role` VARCHAR(20) NULL
- `action` VARCHAR(120) NOT NULL, indexed
  (vd: `auth.register|login|refresh|logout`,
  `admin.user_status.update`, `admin.user_role.update`,
  `admin.category.create|update|delete`, `admin.destination.create|bulk_create|update|delete`)
- `target_type` VARCHAR(80) NULL, `target_id` VARCHAR(120) NULL
- `status` VARCHAR(20) NOT NULL DEFAULT `success`
- `request_id` VARCHAR(64) NULL, indexed
- `method`, `path`, `ip_address`, `user_agent`, `payload` JSON NULL
- `created_at` TIMESTAMPTZ NOT NULL DEFAULT NOW()

## 4. Ràng buộc nghiệp vụ cốt lõi

- Mỗi user chỉ có 1 rating cho 1 destination (`ratings` composite PK).
- Mỗi user favorite 1 destination tối đa 1 lần (`favorites` composite PK + soft delete).
- `rating_avg` của destination được cập nhật sau khi rating tạo/sửa/xóa.

## 5. Quy tắc merge insight

`final_data = merge(human_override, score_snapshot)`

Ưu tiên:
1. Nếu field có trong `human_override`, dùng giá trị đó.
2. Nếu không có override, dùng từ `score_snapshot` đã normalize.
3. Ghi kết quả cuối vào `final_data` để frontend đọc nhanh.

## 5.1 Cập nhật mới về Insight

- Insight được tạo khi destination mới được thêm (baseline 50).
- Khi có rating mới/cập nhật, insight tự động được cập nhật theo cache.
- `insight_cache` lưu sum/count theo dimension và `total_reviews` để tính nhanh O(1).
- `final_data` có thêm `status`: `insufficient_data`, `low_confidence`, `reliable`.

## 6. Index đề xuất

- `idx_destinations_filter` trên (`status`, `price_level`, `rating_avg`, `open_hour`)
- `idx_category_destinations_category` trên (`category_id`, `destination_id`)
- `idx_ratings_destination_score` trên (`destination_id`, `rating_score`)
- `idx_favorites_destination_created` trên (`destination_id`, `created_at`)
- `idx_destinations_slug` unique (`slug`)

## 7. Transaction guideline

- Favorite/unfavorite dùng transaction ngắn, idempotent.
- Rating update gồm:
  1. Upsert rating
  2. Recompute `rating_avg`
  3. Publish event

## 8. Migration guideline

- Dùng migration tool thống nhất (Alembic).
- Không sửa migration cũ ở môi trường production.
- Mọi thay đổi schema phải có rollback rõ ràng.
