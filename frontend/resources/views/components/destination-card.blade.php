@php
    $primaryImage = $destination['img_url'] ?? null;
    if (!$primaryImage && is_array($destination['img_urls'] ?? null)) {
        $primaryImage = collect($destination['img_urls'])->first();
    }

    $categoryNames = collect($destination['categories'] ?? [])->pluck('name')->filter()->values();
    $priceText = $destination['price']['raw_text'] ?? ($destination['price_raw_text'] ?? null);
    $openHours = $destination['open_hours']['raw_text'] ?? ($destination['open_hour'] ?? 'N/A');
    $primaryCategory = $categoryNames->first() ?? 'Điểm đến';
    $isFavorite = (bool) ($isFavorite ?? ($destination['is_favorite'] ?? false));
@endphp

<article class="destination-card">
    <div class="destination-card-media">
        @if ($primaryImage)
            <img src="{{ $primaryImage }}" alt="{{ $destination['name'] }}">
        @else
            <div class="card-image-placeholder">
                <span>No image</span>
            </div>
        @endif

        <div class="destination-card-overlay"></div>

        <div class="destination-card-top">
            <span class="destination-card-chip">{{ ucfirst($primaryCategory) }}</span>
        </div>

        <div class="destination-card-rating">
            ⭐ {{ number_format((float) ($destination['rating_avg'] ?? 0), 1) }}
        </div>

        @if (!empty($destination['id']))
            <form
                method="POST"
                action="{{ route('favorites.add', ['destinationId' => $destination['id']]) }}"
                data-favorite-form
                data-destination-id="{{ $destination['id'] }}"
                data-favorite-add-url="{{ route('favorites.add', ['destinationId' => $destination['id']]) }}"
                data-favorite-remove-url="{{ route('favorites.remove', ['destinationId' => $destination['id']]) }}"
                data-favorited="{{ $isFavorite ? 'true' : 'false' }}">
                @csrf
                <button
                    type="submit"
                    class="favorite-btn"
                    aria-label="{{ $isFavorite ? 'Xoá khỏi danh sách yêu thích' : 'Thêm vào danh sách yêu thích' }}"
                    data-favorite>
                    <span class="favorite-icon">♥</span>
                    <span class="favorite-text">{{ $isFavorite ? 'Đã yêu thích · Nhấn để bỏ' : 'Thêm vào danh sách yêu thích !' }}</span>
                </button>
            </form>
        @else
            <button type="button" class="favorite-btn" aria-label="Thêm vào danh sách yêu thích" data-favorite disabled>
                <span class="favorite-icon">♥</span>
                <span class="favorite-text">Thêm vào danh sách yêu thích !</span>
            </button>
        @endif
    </div>

    <div class="destination-card-body">

        <h3 class="destination-card-title">
            {{ $destination['name'] }}
        </h3>

        <div class="destination-card-meta">
            @if ($priceText)
                <span class="meta-pill meta-pill-price">{{ $priceText }}</span>
            @endif
            <span class="meta-pill">⏱ {{ Str::limit($openHours, 24) }}</span>
        </div>

        <p class="destination-card-description">
            {{ Str::limit($destination['description'] ?? 'Chưa có mô tả', 120) }}
        </p>

        <div class="destination-card-footer">
            <div class="card-action-row">
                <button
                    type="button"
                    class="quick-view-btn"
                    data-open-destination
                    data-destination-id="{{ $destination['id'] }}"
                    aria-label="Chi tiết {{ $destination['name'] }}">
                    Xem chi tiết <span class="arrow">→</span>
                </button>
            </div>
        </div>
    </div>
</article>
