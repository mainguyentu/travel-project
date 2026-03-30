<article class="destination-card">
    <div class="destination-card-media">
        @if ($destination['img_url'] ?? null)
            <img src="{{ $destination['img_url'] }}" alt="{{ $destination['name'] }}">
        @else
            <div class="card-image-placeholder">
                <span>No image</span>
            </div>
        @endif

        <div class="overlay"></div>

        <div class="destination-card-rating">
            ⭐ {{ number_format((float) ($destination['rating_avg'] ?? 0), 1) }}
        </div>
    </div>

    <div class="destination-card-body">
        <h3 class="destination-card-title">
            {{ $destination['name'] }}
        </h3>

        <p class="destination-card-description">
            {{ Str::limit($destination['description'] ?? 'Chưa có mô tả', 80) }}
        </p>

        <div class="destination-card-footer">
            <span class="time">⏱ {{ $destination['open_hour'] ?? 'N/A' }}</span>

            <div class="card-action-row">
                <button
                    type="button"
                    class="quick-view-btn"
                    data-open-destination
                    data-destination-id="{{ $destination['id'] }}"
                    aria-label="Chi tiết {{ $destination['name'] }}">
                    Chi tiết
                </button>
            </div>
        </div>
    </div>
</article>
