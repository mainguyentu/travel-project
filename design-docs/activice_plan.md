# Kế hoạch mở rộng hệ thống với service activice

Tài liệu này là khung sường dùng để tạo tài liệu kỹ thuật cho service mới của hệ thống Travel - Hoạt động du lịch
Tài liệu kỹ thuật được lưu trữ vào thư mục design-docs/
## Chuẩn hoá data (quan trọng nhất)

Đang có:
- `destinations`
- `insight` (scenery, accessibility, crowd, value)

Bổ sung thêm:
### 1.1 Activity Tag (core)
Tạo bảng:

    activities
        - id
        - name
        - slug

    destination_activity (pivot)
        - destination_id
        - activity_id
        - weight (optional)

Mapping ví dụ:

    Chill biển → beach, resort, cafe view biển
    Khám phá thiên nhiên → núi, rừng, thác, trekking
    City tour → landmark, phố, trung tâm
    Food tour → quán ăn, chợ, street food
    Văn hoá - lịch sử → di tích, bảo tàng

Không nên hardcode logic trong code → phải data-driven qua DB

### 1.2 Feature bổ sung

Để recommendation tốt hơn, thêm:

    destination_features
    - is_indoor
    - is_outdoor
    - suitable_time (day/night)
    - budget_level
    - duration_suggested

## Mapping từ Activity → Query logic

### 2.1 Rule-based scoring

Ví dụ:

Chill biển – thư giãn
- scenery: cao
- crowd: thấp
- value: trung bình+
- tag: beach, cafe, resort

Food tour
- value: cao
- crowd: trung bình+
- tag: food, local

## Ranking algorithm (core của hệ thống)

### 3.1 Base score

    score = w1*scenery + w2*accessibility + w3*(1 - crowd) + w4*value
→ crowd phải đảo ngược tùy activity

### 3.2 Activity weight

Ví dụ:

    final_score = base_score * activity_match_weight

Trong đó:
- match 100% → 1.0
- match gần → 0.7
- không match → loại

### 3.3 Personalization (optional)

Sau này:

- user thích nature → boost nature
- user hay chọn food → boost food

## Output structure (API response)

Nên trả về dạng

``` json
{
  "activity": "food-tour",
  "highlight_destinations": [],
  "recommended_destinations": [],
  "trending": []
}
```

### 4.1 Highlight (địa điểm chú ý)
Logic:
- top score cao nhất
- hoặc có human_override

### 4.2 Recommended list
- sort theo score
- pagination

### 4.3 Trending
Dựa vào:
- số lượt view
- số rating gần đây

## Kiến trúc service

Nên tách riêng:

ActivityService
- getDestinationsByActivity(activity_slug)

RecommendationEngine
- calculateScore(destination, activity)
- rank(destinations)

## Flow tổng thể

    User chọn Activity
        ↓
    Fetch destinations theo tag
        ↓
    Apply scoring (insight + rule)
        ↓
    Sort + ranking
        ↓
    Split: highlight / recommend / trending
        ↓
    Return API

## Sai lầm nên tránh
❌ Hardcode logic activity trong controller

❌ Chỉ filter theo category

❌ Không có scoring → list sẽ rất "flat"

❌ Không tách recommendation engine

## Gợi ý roadmap implement

**1.** Tạo bảng activities + pivot

**2.** Mapping dữ liệu cơ bản

**3.** Viết ActivityService

**4.** Implement scoring đơn giản

**5.** Thêm highlight logic

**6.** Optimize + caching
