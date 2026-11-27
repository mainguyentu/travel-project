# 01 - System Architecture

## 1. Mục tiêu kiến trúc

Thiết kế kiến trúc microservice cho Alats Travel DaNang nhằm:
- Đáp ứng MVP nhanh nhưng vẫn có khả năng mở rộng.
- Tách domain rõ ràng: auth, destination, interaction, admin, analytics.
- Đảm bảo hiệu năng mục tiêu: p95 < 200ms.

## 2. Kiến trúc logic tổng thể

### 2.1 Thành phần chính
- **Client Layer**
  - Public frontend (Laravel Blade + JS)
  - Admin frontend (luồng quản trị riêng)
- **Edge Layer**
  - Load Balancer
  - API Gateway (FastAPI): auth middleware, routing, rate limiting, tracing
- **Service Layer (FastAPI microservices)**
  - Auth Service
  - Destination Service
  - Interaction Service (favorites/ratings)
  - Admin Service
  - Analytics Service
- **Data & Infra Layer**
  - PostgreSQL (dữ liệu quan hệ)
  - Redis (cache, session hỗ trợ, rate limit, realtime counters)
  - Elasticsearch (full-text search + suggestion)
  - Kafka (event bus cho đồng bộ bất đồng bộ)
  - Worker Service (consumer Kafka)

### 2.2 Nguyên tắc kết nối
- Client chỉ gọi qua API Gateway.
- Service không truy cập DB của service khác trực tiếp.
- Đồng bộ chéo domain dùng event Kafka, không gọi sync chéo nếu không cần thiết.

## 3. Phân tách domain (bounded context)

### 3.1 Auth Domain
- Quản lý đăng ký/đăng nhập/refresh token/revoke token.
- Quản lý role và status user.

### 3.2 Destination Domain
- Quản lý điểm đến, category, dữ liệu insight.
- Cung cấp API list/filter/detail.

### 3.3 Interaction Domain
- Quản lý favorite và rating của user.
- Đảm bảo idempotent cho favorite và unique rating/user/destination.

### 3.4 Admin Domain
- CRUD destination, user, category.
- Dashboard thống kê top địa điểm.

### 3.5 Analytics Domain
- Tổng hợp dữ liệu yêu thích/rating/view từ event stream.
- Trả dữ liệu ranking/dashboard cho admin.

## 4. Data flow quan trọng

### 4.1 Public list/detail
1. Frontend gọi Gateway `/api/v1/destinations`.
2. Gateway xác thực (nếu cần) và route sang Destination Service.
3. Destination Service query PostgreSQL + cache Redis.
4. Trả dữ liệu cho client.

### 4.2 Favorite/Rating
1. User gọi endpoint interaction có JWT.
2. Interaction Service ghi DB transaction.
3. Publish event Kafka (`favorite.created`, `rating.updated`).
4. Analytics/Worker consume để cập nhật bảng tổng hợp + Redis realtime metrics.

### 4.3 Search sync
1. Destination update tại Admin Service.
2. Phát event `destination.updated`.
3. Worker consume và đồng bộ index sang Elasticsearch.

## 5. Caching strategy (Redis)

- Cache list destination theo filter key:
  - `destinations:list:{category}:{price}:{rating}:{page}:{sort}`
- Cache detail destination:
  - `destination:detail:{id}`
- Cache dashboard top list:
  - `admin:top:favorites`, `admin:top:ratings`, `admin:top:views`
- Invalidation theo event sau khi update destination/rating/favorite.

## 6. Khả năng mở rộng và độ tin cậy

- Horizontal scale cho API Gateway và các service stateless.
- Connection pool cho PostgreSQL + Redis.
- Retry + DLQ cho consumer Kafka.
- Backup PostgreSQL định kỳ + kiểm tra restore.

### 6.1 Connection Pooling Strategy (chi tiết)

Mục tiêu:
- Giảm chi phí tạo kết nối mới cho mỗi request.
- Ổn định latency p95 khi tải tăng.
- Tránh lỗi nghẽn do mở quá nhiều kết nối đồng thời.

Phạm vi pooling:
- **Edge/Gateway (Nginx)**:
  - Duy trì keepalive giữa gateway và từng backend upstream.
  - Dùng `proxy_http_version 1.1` và `Connection ""` để tái sử dụng TCP connection.
- **Backend -> PostgreSQL (SQLAlchemy)**:
  - Bắt buộc bật engine pool và `pool_pre_ping`.
  - Cần cấu hình tường minh theo env: `pool_size`, `max_overflow`, `pool_timeout`, `pool_recycle`.
- **Backend -> Redis**:
  - Dùng Redis connection pool (không tạo client mới cho từng request).
  - Cấu hình giới hạn connection theo tải và timeout phù hợp.
- **Frontend -> API Gateway**:
  - HTTP client tái sử dụng connection và giới hạn concurrency hợp lý cho request burst.

Nguyên tắc sizing (MVP):
- Pool DB bắt đầu nhỏ, tăng dần theo CPU và throughput thực đo.
- Tổng số kết nối DB của toàn bộ service không vượt ngưỡng an toàn của PostgreSQL.
- Redis pool ưu tiên độ ổn định và timeout ngắn để fail-fast.

Acceptance criteria:
- Không có cảnh báo `connection pool exhausted` trong điều kiện tải mục tiêu.
- p95 latency không tăng đột biến khi tăng request đồng thời trong ngưỡng thiết kế.
- Có dashboard theo dõi: active connections, wait time, pool timeout, error rate.

## 7. Observability

- Log chuẩn JSON (request_id, user_id, service, latency).
- Metrics: RPS, p95 latency, error rate, DB query time, cache hit ratio.
- Tracing xuyên service qua correlation id.

## 8. Decision log (MVP)

- Chọn REST `/api/v1` để đơn giản hóa integration frontend.
- Chọn Kafka + Elasticsearch ngay MVP vì yêu cầu search nâng cao và analytics async đã được chốt.
- Giữ module boundary rõ nhưng có thể deploy gộp trong giai đoạn đầu để tối ưu chi phí.
