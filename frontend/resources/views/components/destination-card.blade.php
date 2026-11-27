@props(['destination'])
@php
    $img = $destination['img_url'] ?? null;
    $initial = mb_substr($destination['name'] ?? '?', 0, 1);
@endphp
<article class="card">
    <div class="card-img">
        @if ($img)
            <img src="{{ $img }}" alt="{{ $destination['name'] ?? '' }}" loading="lazy">
        @else
            <div class="ph">{{ $initial }}</div>
        @endif
        <span class="rating-badge">★ {{ $destination['rating_avg'] ?? 0 }}</span>
    </div>
    <div class="card-body">
        <h3>{{ $destination['name'] ?? '' }}</h3>
        <p class="muted">{{ $destination['address'] ?? '' }}</p>
        @if (! empty($destination['description']))
            <p class="muted">{{ \Illuminate\Support\Str::limit($destination['description'], 90) }}</p>
        @endif
        <div class="card-meta">
            <span class="chip">{{ $destination['price_level'] ?? '' }} · {{ $destination['view_count'] ?? 0 }} lượt xem</span>
            <span class="card-actions">
                <button type="button" class="link-btn" data-detail="{{ $destination['id'] ?? '' }}">Xem chi tiết →</button>
                @if (session('access_token'))
                    <form method="POST" action="{{ route('favorites.add', ['id' => $destination['id'] ?? 0]) }}" class="inline-form">
                        @csrf
                        <button type="submit" class="link-btn">♥ Yêu thích</button>
                    </form>
                @endif
            </span>
        </div>
    </div>
</article>
