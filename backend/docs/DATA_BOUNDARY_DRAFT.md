# Data Boundary Draft by Service

Draft này định nghĩa ranh giới dữ liệu (data ownership) để chuyển từ service-split hiện tại sang microservices thật với ownership rõ ràng, giảm coupling DB.

Cập nhật: 2026-04-26

## 1. Mục tiêu và nguyên tắc

- Mỗi service có **write ownership** trên tập dữ liệu riêng.
- Service khác chỉ đọc dữ liệu qua API/event/read-model, không query chéo bảng write model.
- Dữ liệu tổng hợp/cross-domain đi qua event bus + read model (analytics/reporting).
- Ưu tiên tách theo bounded context trước, tối ưu hạ tầng sau.

## 2. Service ownership (target state)

### 2.1 Auth Service (source of truth cho danh tính + phiên)

- **Own write:**
  - `users` (identity, role, status)
  - `user_tokens` (refresh/session state)
- **Expose cho service khác:**
  - Token verification claims (`sub`, `role`, `status`) qua JWT.
  - Admin identity lookups qua internal API (nếu cần).
- **Không nên:** service khác tự update `users` trực tiếp.

### 2.2 Destination Service (catalog và public discovery)

- **Own write:**
  - `destinations`
  - `categories`
  - `category_destinations`
  - `destination_features`
  - `destination_insights`
- **Consume events:**
  - `DestinationCreated/Updated/Deleted` (internal consistency)
  - Optional projection events từ interaction để enrich ranking.
- **Publish events:**
  - `DestinationCreated`
  - `DestinationUpdated`
  - `DestinationDeleted`
  - `DestinationViewed` (đã có)

### 2.3 Interaction Service (user-to-destination actions)

- **Own write:**
  - `favorites`
  - `ratings`
- **Dependencies:**
  - Cần validate `user_id` (JWT/Auth)
  - Cần validate `destination_id` tồn tại (Destination API hoặc local projection)
- **Publish events:**
  - `FavoriteCreated`
  - `FavoriteDeleted`
  - `RatingUpserted`

### 2.4 Analytics Service (read-optimized aggregate model)

- **Own write:**
  - `destination_metrics` (aggregate projection)
  - Search index (`elasticsearch`) cho analytics/search read use-cases
- **Input duy nhất (target):**
  - Event stream từ interaction + destination + view events
- **Không nên:** update write model của destination/interaction.

### 2.5 Admin Service (orchestration/BFF cho admin)

- **Own write (target):**
  - Không sở hữu domain table riêng ở phase đầu.
- **Vai trò:**
  - Orchestrate command sang Auth/Destination service.
  - Ghi audit trail tập trung.
- **Own write hợp lệ:**
  - `audit_logs` (nếu giữ centralized audit trong giai đoạn chuyển đổi).

## 3. Bảng hiện tại -> ownership đề xuất

- `users` -> Auth
- `user_tokens` -> Auth
- `categories` -> Destination
- `destinations` -> Destination
- `category_destinations` -> Destination
- `destination_features` -> Destination
- `destination_insights` -> Destination
- `favorites` -> Interaction
- `ratings` -> Interaction
- `destination_metrics` -> Analytics
- `audit_logs` -> Admin (hoặc platform-audit service về sau)

## 4. API boundary rules (bắt buộc)

- `auth-service`:
  - Không được ghi vào destination/interaction tables.
- `destination-service`:
  - Không được ghi vào `favorites`, `ratings`, `destination_metrics`.
- `interaction-service`:
  - Không được ghi vào `destinations`, `categories`, `destination_metrics`.
- `analytics-service`:
  - Chỉ ghi projection (`destination_metrics`, index), không mutate domain write models.
- `admin-service`:
  - Không ghi trực tiếp domain table ngoài audit (target), chỉ gọi command APIs.

## 5. Read model và integration pattern

- **User-facing listing/ranking:**
  - Short term: Destination service có thể đọc local fields + optional analytics API.
  - Target: dùng projection phục vụ query nặng (top/ranking/search) thay vì join xuyên domain.
- **Validation foreign keys xuyên domain:**
  - Dùng synchronous API check tại command boundary hoặc local projection table.
  - Tránh DB foreign key cứng giữa service-owned databases khi tách vật lý.
- **Consistency model:**
  - Command path: strong consistency trong cùng service DB.
  - Cross-service aggregates: eventual consistency qua Kafka.

## 6. Lộ trình tách boundary (đề xuất triển khai)

### Phase 1 - Logical boundary trong cùng DB (ngay)

- Gắn ownership rõ ràng cho từng table (theo mục 3).
- Cấm repository/service truy cập bảng ngoài ownership trừ read-only projection được cho phép.
- Chuẩn hóa event contract và idempotency key cho consumer.

Trạng thái triển khai trong codebase:

- Đã thêm runtime boundary guard ở tầng repository, kiểm tra theo `SERVICE_PROFILE`.
- Mỗi service container được gán profile riêng (`auth-service`, `destination-service`, `interaction-service`, `admin-service`, `analytics-service`, `worker-service`).
- Khi repository bị dùng sai boundary, hệ thống raise `BOUNDARY_VIOLATION` để fail-fast.

### Phase 2 - API-first boundary

- Admin chuyển từ direct repository call sang internal API call đến Auth/Destination.
- Interaction validate destination qua Destination API/projection thay vì đọc thẳng bảng.
- Analytics chỉ nhận event, không đọc write model tables trực tiếp.

Trạng thái triển khai trong codebase (Phase 2):

- `admin-service`: đã chuyển các luồng Admin (users/categories/destinations) sang gọi internal APIs từ `auth-service`/`destination-service`; stats gọi `analytics-service`.
- `auth-service`: thêm internal admin endpoints để list/update users (`/internal/admin/users`, ...).
- `destination-service`: thêm internal admin endpoints cho categories/destinations và internal read endpoints cho validate/batch destinations.
- `interaction-service`: không query thẳng `destinations` khi validate/list favorites; dùng destination internal endpoints (`/internal/destinations/...`).
- `analytics-service`: query chỉ trên projection `destination_metrics` (không join `destinations`), enrich destination data qua destination internal batch endpoint.
- Tighten boundary: đã loại bỏ `admin-service` khỏi allowed profiles của Destination/Category repositories; loại bỏ `admin-service`/`interaction-service` khỏi User repository.

### Phase 3 - Physical split

- Tách DB/schema per service.
- Migration projection pipelines và backfill metric/index.
- Gắn contract test cho event schema + service APIs.

## 7. Rủi ro chính và biện pháp

- **Rủi ro:** Duplicate logic khi chuyển từ repository nội bộ sang API call.
  - **Giảm thiểu:** tách application service layer, giữ command handlers rõ ràng.
- **Rủi ro:** Event ordering/replay làm sai aggregate.
  - **Giảm thiểu:** idempotent consumer + versioned event + DLQ replay runbook.
- **Rủi ro:** Query chậm khi bỏ join trực tiếp.
  - **Giảm thiểu:** read model chuyên biệt, materialized aggregates.

## 8. Checklist review cho mỗi PR kiến trúc

- PR có thêm truy cập chéo bảng ngoài ownership không?
- Có phát sinh event mới? Event đã version + có consumer idempotency chưa?
- Có thay đổi API contract giữa service? Đã có backward compatibility plan chưa?
- Có update docs boundary/ADR tương ứng chưa?

