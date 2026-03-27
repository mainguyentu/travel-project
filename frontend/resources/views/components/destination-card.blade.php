<article class="destination-card">
    <div class="destination-card-media">
        @if ($destination['img_url'] ?? null)
            <img src="{{ $destination['img_url'] }}" alt="{{ $destination['name'] }}">
        @else
            <div class="card-image-placeholder">
                <span class="placeholder-text">No image</span>
            </div>
        @endif

        <span class="destination-card-rating">⭐ {{ number_format((float) ($destination['rating_avg'] ?? 0), 1) }}</span>

        @if (session()->has('access_token'))
            <button class="favorite-btn @if($destination['is_favorited'] ?? false) favorited @endif" 
                    data-destination-id="{{ $destination['id'] }}">
                ❤
            </button>
        @endif
    </div>

    <div class="destination-card-body">
        <h3 class="destination-card-title">
            <a href="{{ route('destinations.show', $destination['id']) }}">
                {{ $destination['name'] }}
            </a>
        </h3>

        <p class="destination-card-subtitle">📍 {{ $destination['address'] ?? 'Địa chỉ không xác định' }}</p>

        <div class="destination-card-meta">
            <span class="rating">
                Đánh giá: {{ number_format((float) ($destination['rating_avg'] ?? 0), 1) }}/5
            </span>
            <span class="price-level">
                @php
                    $priceLevels = ['miễn phí' => '$', 'thấp' => '$', 'trung bình' => '$$', 'cao' => '$$$'];
                @endphp
                Mức giá: {{ $priceLevels[$destination['price_level'] ?? 'trung bình'] ?? '$$' }}
            </span>
        </div>

        <p class="destination-card-description">
            {{ Str::limit($destination['description'] ?? '', 100) }}
        </p>

        <div class="card-action-row">
            <a href="{{ route('destinations.show', $destination['id']) }}" class="btn-primary">
                Xem chi tiết
            </a>
        </div>
    </div>
</article>
