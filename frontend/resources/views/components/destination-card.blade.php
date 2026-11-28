@props(['destination', 'favorited' => false])
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
        @if (session('access_token'))
            @if ($favorited)
                <form method="POST" action="{{ route('favorites.remove', ['id' => $destination['id'] ?? 0]) }}" class="fav-overlay">
                    @csrf
                    @method('DELETE')
                    <button type="submit" class="fav-heart is-fav" aria-label="Bỏ yêu thích" title="Bỏ yêu thích">♥</button>
                </form>
            @else
                <form method="POST" action="{{ route('favorites.add', ['id' => $destination['id'] ?? 0]) }}" class="fav-overlay">
                    @csrf
                    <button type="submit" class="fav-heart" aria-label="Thêm vào yêu thích" title="Yêu thích">♥</button>
                </form>
            @endif
        @endif
    </div>
    <div class="card-body">
        <h3>{{ $destination['name'] ?? '' }}</h3>
        <p class="muted">{{ $destination['address'] ?? '' }}</p>
        @if (! empty($destination['description']))
            <p class="muted card-desc">{{ \Illuminate\Support\Str::limit($destination['description'], 90) }}</p>
        @endif
        <div class="card-meta">
            <span class="chip">{{ $destination['price_level'] ?? '' }} · {{ $destination['view_count'] ?? 0 }} lượt xem</span>
            <span class="card-actions">
                <button type="button" class="link-btn" data-detail="{{ $destination['id'] ?? '' }}">Xem chi tiết →</button>
            </span>
        </div>
    </div>
</article>
