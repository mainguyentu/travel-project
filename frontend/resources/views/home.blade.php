@extends('layouts.public')

@section('title', 'Alats Travel Đà Nẵng')

@section('content')
<section class="hero">
    <div>
        <h1>Khám phá <span style="color:#7DD3FC">Đà Nẵng</span></h1>
        <p class="lead">Thành phố đáng sống nhất Việt Nam — nơi biển xanh hòa quyện với núi non hùng vĩ</p>
        <form class="search-box" role="search" aria-label="Tìm kiếm điểm đến" method="GET" action="{{ route('destinations.index') }}">
            <label class="sr-only" for="hero-q">Từ khóa tìm kiếm</label>
            <input id="hero-q" type="text" name="q" placeholder="Tìm điểm đến, hoạt động, ẩm thực…" value="{{ request('q') }}">
            <button type="submit" class="btn">Tìm kiếm</button>
        </form>
    </div>
</section>

<div class="container">
    @if (! empty($landing['categories']))
    <section class="section">
        <div class="section-head">
            <h2>Hoạt động <span class="grad-text">du lịch</span></h2>
            <p>Đa dạng các hoạt động thú vị cho mọi lứa tuổi và sở thích</p>
        </div>
        <div class="cats">
            @foreach ($landing['categories'] as $c)
                <a class="chip" href="{{ route('destinations.index', ['category_slug' => $c['slug'] ?? '']) }}">{{ $c['name'] ?? '' }} ({{ $c['count'] ?? 0 }})</a>
            @endforeach
        </div>
    </section>
    @endif

    <section class="section">
        <div class="section-head">
            <h2>Điểm đến <span class="grad-text">nổi bật</span></h2>
            <p>Khám phá những địa danh du lịch nổi tiếng và hấp dẫn nhất tại Đà Nẵng</p>
        </div>
        <div class="grid">
            @foreach ($landing['highlights'] ?? [] as $d)
                <x-destination-card :destination="$d" :favorited="in_array($d['id'] ?? 0, $favoriteIds ?? [])" />
            @endforeach
        </div>
    </section>

    <section class="section section-alt">
        <div class="section-head">
            <h2>Rating <span class="grad-text">cao</span></h2>
            <p>Những điểm đến được du khách đánh giá cao nhất</p>
        </div>
        <div class="grid">
            @foreach ($landing['top_ratings'] ?? [] as $d)
                <x-destination-card :destination="$d" :favorited="in_array($d['id'] ?? 0, $favoriteIds ?? [])" />
            @endforeach
        </div>
    </section>

    <section class="hero" style="min-height:44vh;margin-top:3rem;background:var(--grad-sand)">
        <div>
            <h2 style="font-size:clamp(1.6rem,4vw,2.6rem);margin:0 0 0.6rem">Trải nghiệm <span style="color:#E4C69A">cao cấp</span> bên vịnh biển</h2>
            <p class="lead">Tour du thuyền, nghỉ dưỡng và ẩm thực tuyển chọn</p>
            <a class="btn" href="{{ route('destinations.index', ['sort' => 'rating']) }}">Khám phá ngay</a>
        </div>
    </section>

    <section class="section">
        <div class="section-head">
            <h2>Được <span class="grad-text">yêu thích</span></h2>
            <p>Lưu lại hành trình của cộng đồng du khách</p>
        </div>
        <div class="grid">
            @foreach ($landing['top_favorites'] ?? [] as $d)
                <x-destination-card :destination="$d" :favorited="in_array($d['id'] ?? 0, $favoriteIds ?? [])" />
            @endforeach
        </div>
        <x-destination-detail-modal />
    </section>
</div>
@endsection

@push('scripts')
<script>
// Trang chủ cũng cần API_BASE cho modal chi tiết (như destinations/index).
window.API_BASE = @json(url('/api/v1'));
</script>
@endpush
