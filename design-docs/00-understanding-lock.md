# 00 - Understanding Lock (Đã xác nhận)

## Mục tiêu sản phẩm

Xây dựng website **Alats Travel DaNang** theo kiến trúc microservice, tập trung vào trải nghiệm khám phá địa điểm du lịch và quản trị nội dung địa điểm.

## Phạm vi MVP

- Public frontend: landing, danh sách địa điểm, chi tiết địa điểm.

- Bộ lọc danh sách: thể loại, mức giá, rating.

- Auth: đăng ký, đăng nhập, refresh token.

- User action: yêu thích địa điểm, rating địa điểm.

- Admin dashboard (luồng quản trị riêng): quản lý địa điểm, user, thể loại; thống kê top địa điểm theo yêu thích, rating, lượt xem.

## Vai trò người dùng

- Guest: xem landing, xem/lọc danh sách, xem chi tiết.

- User: toàn bộ quyền Guest + yêu thích/rating.

- Admin: CRUD quản trị + xem thống kê.

## Stack công nghệ đã chốt

- Backend: Python + FastAPI (microservices theo domain).

- Frontend public: Laravel + HTML/CSS/JS.

- Admin dashboard: luồng frontend quản trị riêng, đi qua Admin BFF/API admin.

- Vận hành: Docker + Docker Compose.

- Triển khai: CI/CD pipeline tự động build/test/deploy.

- Cơ sở dữ liệu quan hệ: PostgreSQL – Dùng cho dữ liệu có cấu trúc chặt chẽ.

- Cache: Redis – Cache kết quả truy vấn, session, rate limiting, hàng đợi tác vụ nhẹ.

- API: RESTful – Thiết kế endpoint ngắn gọn, tường minh, dùng HTTP methods chuẩn.

- Bảo mật - Xác thực: sử dụng JWT + OAuth2.

- Search Engine + Message queue: Elasticsearch – Tìm kiếm nâng cao, full-text, gợi ý + Kafka – Xử lý bất đồng bộ (thông báo, đồng bộ dữ liệu search, đồng bộ thống kê).

- Realtime Analytic: Redis.

- SỬ dụng Connection Pool để quản lý, phân phối request.

## Non-functional requirements đã chốt

- Performance: Thời gian phản hồi API < 200ms cho 95% requests.

- Scale mục tiêu MVP: 1k MAU, 10k địa điểm, 20 req/s peak.

- Security: Mã hóa mật khẩu (bcrypt), HTTPS, chống SQL injection, XSS, CSRF, rate limiting, JWT an toàn, OAuth2 tích hợp.

- Reliability: Hệ thống hoạt động 24/7, backup dữ liệu định kỳ, có cơ chế fallback.

## Kiến trúc hệ thống

Hệ thống theo hướng microservice:

- Client: gọi API qua HTTPS.

- Load balance: phân phối các request đến service tương ứng.

- API geteway: FastAPI với middleware - xử lý xác thực, routing, rate limit.

- App Layer: FastAPI app, chia thành các module.

- Service Layer: chứa logic nghiệp vụ, tương tác với các data và service ngoài.

- Data Layer: Repository pattern, tương tác với PostgreSQL, Redis Cache.

- Cache Layer: Redis.

- Search enginer + Message Queue: Elasticsearch cluster, đồng bộ dữ liệu qua Kafka + Kafka cho các tác vụ nền.

- Worker Service: Consumer Python (FastAPI background tasks hoặc Celery) xử lý Kafka messages.

## Thiết kế cơ sở dữ liệu (PostgreSQL)

các bảng chính bao gồm: user, user_token, categories, category_destination, destinations, destination_insights, favorites, ratings.

- user: id(PK), name, email(unique), password_hash, role(user/admin), status(active/locked), created_at, updated_at

- user_token: id(PK), user_id(FK), token_access, refresh_token, revoked_at, created_at.

- categories: id(PK), name, slug(unique), desciptions, created_at, updated_at.

- category_destination: category_id(PK), destination_id(PK).

- destinations: id(PK), name, slug(unique), address, description, rating_avg, lat, lng, price_level, open_hour, img_url, url_map, created_at, updated_at.

- destination_insights: destination_id(PK), human_override(json, nullable), score_snapshot(json, nullable), final_data (json), insight_cache (json, nullable), updated_at
- favorites: user_id(PK), destination_id(PK), created_at, deleted_at.

- ratings: user_id(PK), destination_id(PK), rating_score(1..5), comment, created_at, updated_at.

Quy tắc hợp nhất dữ liệu:

- final_data = `human_override + score_snapshot` theo quy tắc kết hợp

Ví dụ mẫu cấu trúc `score_snapshot`:

- scores.crowd_level.value

- scores.crowd_level.confidence

- scores.crowd_level.source_count

- scores.crowd_level.agreement

Ví dụ mẫu cấu trúc `final_data`:

- should_go (boolean)

- best_time (array: morning/afternoon/evening)

- crowd_level (low/medium/high)

- cost (free/low/medium/high)

- highlights (array string)

- downsides (array string)

- summary (string)

- nearby_places (array place_id hoặc object rút gọn)

## Một số quan hệ nghiệp vụ

- User 1 - 1 User_token

- Category N - N Destination thông qua bảng category_destinations

- Destination 1 - 1 Destination_insight

- Destination 1 - N Favorite , User 1 - N Favorite

- Destination 1 - N Rating , User 1 - N Rating

## Index kiến nghị (có thể bổ sung)

- destinations(status, price_level, rating_avg, open_hour)

- category_destination(category_id, destination_id)

- ratings(destination_id, rating_score)

- favorites(destination_id, created_at)

## Quy tắc nghiệp vụ cốt lõi

- Mỗi user chỉ có 1 rating cho 1 địa điểm (cho phép cập nhật rating cũ).

- Mỗi user chỉ yêu thích 1 lần cho 1 địa điểm (idempotent).

## Giả định hiện tại

- Frontend public và admin dashboard là 2 luồng UI tách biệt.

- API theo chuẩn REST, version hóa qua prefix /api/v1.

- Rewrite 2026-11-27 (P0, owner đã chốt): MVP chạy **monolith FastAPI**
  (`app.main:app`) trước, gateway chỉ proxy 1 backend; tách microservice
  theo domain ở pha sau. Lý do: nhanh, ít rủi ro, giữ nguyên contract URL.

- Rewrite 2026-11-27 (P0, owner đã chốt): `destination_insights` tối giản
  trong MVP — chỉ `destination_id` PK + `final_data` JSON + `updated_at`;
  bỏ `human_override/score_snapshot/insight_cache` pha đầu, thêm lại ở pha async.

- Rewrite 2026-11-27 (P0, owner đã chốt): search pha đầu dùng **DB LIKE**,
  chưa Elasticsearch/Kafka/worker; thêm lại ở pha async.

## Yêu cầu giao diện

Giao diện dashboard quản lý admin: mong đợi giao diện dễ thao tác, đầy đủ chức năng.

Giao diện client frontend:

- Yêu cầu thiết kế theo quy chuẩn laravel blade.

- Chia component rõ ràng, tái sử dụng view chung một cách hợp lý.

- Thiết kế màu sắc hợp lý, hài hoà không quá chói mắt.

- Cấu trúc file rõ ràng, css và script tách thành file riêng không viết inline trong html.

- Layout hiện đại, thể hiện rõ không khí của một trang web về một thành phố du lịch.

- Không quá lạm dụng các radius bo góc, sử dụng một cách hợp lý.

- Ưu tiên sử dụng các màu gradient mang phong cách tươi mát của thành phố biển.
