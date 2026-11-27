# 04 - Workflows

## 1. Workflow người dùng Guest

1. Truy cập landing page.
2. Xem danh sách địa điểm nổi bật.
3. Đi tới trang danh sách địa điểm.
4. Lọc theo category, mức giá, rating.
5. Xem trang chi tiết địa điểm.
6. Click đăng nhập khi muốn favorite/rating.

## 2. Workflow người dùng User

### 2.1 Đăng ký/đăng nhập
1. Mở trang đăng ký/đăng nhập.
2. Submit form.
3. Nhận access token + refresh token.
4. Redirect về trang trước đó hoặc trang profile.

### 2.2 Favorite địa điểm
1. User bấm “Yêu thích” tại card/list/detail.
2. Frontend gọi `POST /me/favorites/{destination_id}`.
3. UI cập nhật trạng thái heart active.

### 2.3 Rating địa điểm
1. User chọn sao 1..5 và nhập comment (tùy chọn).
2. Frontend gọi `PUT /me/ratings/{destination_id}`.
3. UI hiển thị rating cá nhân mới nhất và rating trung bình cập nhật.

## 3. Workflow Admin

### 3.1 Quản lý category
1. Mở dashboard category.
2. Tạo/sửa/xóa category.
3. Hệ thống validate slug unique.

### 3.2 Quản lý destination
1. Mở danh sách destination trong admin.
2. Tạo mới hoặc chỉnh sửa thông tin.
3. Gán category.
4. Lưu và phát event cập nhật search index.

### 3.3 Quản lý user
1. Mở danh sách user.
2. Khóa/mở khóa user.
3. Nâng role user -> admin khi cần.

### 3.4 Xem thống kê
1. Mở dashboard analytics.
2. Xem top favorite, top rating, top view.
3. Lưu ý (theo code hiện tại): chưa có lọc theo khoảng thời gian —
   các số `total_requests/unique_users/...`, `total_reviews/avg_rating` đang hardcode 0.

## 3.5 Activity recommendation trên home (mới — theo code hiện tại)
1. Home đọc `activity_slug` (default `city-tour`, validate trong 5 tabs cố định)
   + 2 feature flag `activity_recommendation_home_enabled`,
   `activity_recommendation_endpoint_enabled`.
2. Nếu bật: gọi `GET /public/activities/{slug}/recommendations?page=1&limit=3`
   → `activity/highlight_destinations/recommended_destinations/trending`.
3. Lỗi gom thành `activityRecommendationError`, home vẫn render landing thường.

## 4. Workflow hệ thống (async)

### 4.1 Event: favorite
- Trigger: favorite tạo/hủy.
- Producer: Interaction Service.
- Consumer: Analytics Worker.
- Output: cập nhật bảng tổng hợp + cache top favorites.

### 4.2 Event: rating
- Trigger: rating tạo/sửa.
- Producer: Interaction Service.
- Consumer: Destination Service + Analytics Worker.
- Output: cập nhật rating_avg + ranking.

### 4.3 Event: destination updated
- Trigger: admin cập nhật destination.
- Producer: Admin Service.
- Consumer: Search Worker.
- Output: reindex document Elasticsearch.

## 5. Failure & retry workflow

- Consumer fail: retry exponential backoff 3 lần.
- Sau retry fail: đưa message vào DLQ.
- Có dashboard theo dõi DLQ và manual replay.

## 6. Session/token workflow

- Access token ngắn hạn.
- Refresh token dài hạn, có revoke.
- Khi refresh thành công, có thể rotate refresh token.
