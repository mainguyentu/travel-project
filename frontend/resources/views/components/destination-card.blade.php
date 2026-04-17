@php
    $primaryImage = $destination['img_url'] ?? null;
    if (!$primaryImage && is_array($destination['img_urls'] ?? null)) {
        $primaryImage = collect($destination['img_urls'])->first();
    }

    $categoryNames = collect($destination['categories'] ?? [])->pluck('name')->filter()->values();
    $priceLevel = $destination['price']['level'] ?? ($destination['price_level'] ?? null);
    $priceLabelMap = [
        'low' => '$ - Tiết kiệm',
        'medium' => '$$ - Vừa phải',
        'high' => '$$$ - Cao cấp',
    ];
    $priceLabel = $priceLabelMap[$priceLevel] ?? 'N/A';
    $openHours = $destination['open_hours']['raw_text'] ?? ($destination['open_hour'] ?? 'N/A');
    $primaryCategory = $categoryNames->first() ?? 'Điểm đến';
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
    </div>

    <div class="destination-card-body">

        <h3 class="destination-card-title">
            {{ $destination['name'] }}
        </h3>

        <div class="destination-card-meta">
            <span class="meta-pill meta-pill-price">{{ $priceLabel }}</span>
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
