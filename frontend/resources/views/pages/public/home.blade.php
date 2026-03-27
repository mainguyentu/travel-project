@extends('layouts.app')

@section('title', 'Home - Alats Travel')

@section('content')
    <section class="home-hero" id="home">
        <div class="site-container home-hero-content">
            <h1>
                Khám phá <span class="text-gradient">Đà Nẵng</span>
            </h1>
            <p>
                Thành phố đáng sống - Nơi biển xanh hòa quyện với núi non hùng vĩ
            </p>

            <form action="{{ route('destinations.index') }}" method="GET" class="hero-search" role="search">
                <input type="text" name="search" placeholder="Tìm kiếm điểm đến, ẩm thực, hoạt động...">
                <button type="submit" class="btn-primary">Tìm kiếm</button>
            </form>

            <div class="hero-quick-links">
                <a href="{{ route('destinations.index') }}" class="btn-ghost">Xem tất cả điểm đến</a>
                <a href="{{ route('destinations.index', ['rating' => 4.5]) }}" class="btn-ghost">Top đánh giá</a>
            </div>
        </div>
        <span class="hero-scroll" aria-hidden="true"></span>
    </section>

    <section class="section-pad" id="destinations">
        <div class="site-container">
            <div class="section-heading">
                <h2>Điểm đến <span class="text-gradient">nổi bật</span></h2>
                <p>
                    Khám phá những địa danh du lịch nổi tiếng và hấp dẫn nhất tại Đà Nẵng
                </p>
            </div>

            <div class="destination-grid">
                @forelse ($featured as $destination)
                    @include('components.destination-card', ['destination' => $destination])
                @empty
                    <div class="empty-state">
                        <p>Chưa có địa điểm nổi bật.</p>
                    </div>
                @endforelse
            </div>
        </div>
    </section>

    <section class="section-pad section-soft-cyan" id="activities">
        <div class="site-container">
            <div class="section-heading">
                <h2>Hoạt động <span class="text-gradient">du lịch</span></h2>
                <p>Đa dạng các hoạt động thú vị cho mọi lứa tuổi và sở thích</p>
            </div>

            <div class="category-grid">
                @forelse ($categories as $category)
                    @php
                        $iconClasses = ['cyan', 'green', 'orange', 'purple'];
                        $iconGlyphs = ['~', '^', '*', 'o'];
                        $idx = $loop->index % 4;
                    @endphp
                    <article class="activity-card">
                        <span class="activity-icon {{ $iconClasses[$idx] }}">{{ $iconGlyphs[$idx] }}</span>
                        <h3 class="activity-title">{{ $category['name'] }}</h3>
                        <p class="muted activity-desc">
                            {{ $category['description'] ?? 'Khám phá những trải nghiệm phù hợp với bạn.' }}</p>
                            <a href="{{ route('destinations.index', ['category_slug' => $category['slug']]) }}"
                            class="btn-secondary">Tìm hiểu thêm</a>
                    </article>
                @empty
                    <div class="empty-state">
                        <p>Chưa có dữ liệu hoạt động.</p>
                    </div>
                @endforelse
            </div>
        </div>
    </section>

    <section class="section-pad" id="cuisine">
        <div class="site-container">
            <div class="section-heading">
                <h2>Ẩm thực <span class="text-gradient">Đà Nẵng</span></h2>
                <p>Khám phá hương vị đặc trưng của ẩm thực miền Trung Việt Nam</p>
            </div>

            @php
                $dishes = [
                    [
                        'name' => 'Mỳ Quảng',
                        'price' => '30.000 - 50.000d',
                        'desc' => 'Mon mi dac trung voi nuoc dung dam da va topping phong phu.',
                    ],
                    [
                        'name' => 'Bún Chả cá',
                        'price' => '35.000 - 60.000d',
                        'desc' => 'Bun tuoi ket hop cha ca thom ngon, huong vi bien rat ro.',
                    ],
                    [
                        'name' => 'Bánh xèo',
                        'price' => '25.000 - 45.000d',
                        'desc' => 'Vo gion, nhan tom thit gia do, an kem rau song thanh mat.',
                    ],
                    [
                        'name' => 'Hải sản tươi',
                        'price' => 'Theo thoi gia',
                        'desc' => 'Lua chon hai san tuoi song va che bien theo nhieu phong cach.',
                    ],
                ];
            @endphp

            <div class="cuisine-layout">
                <article class="cuisine-hero">
                    <img src="https://images.unsplash.com/photo-1696654351863-4d9a6d9cd4b9?auto=format&fit=crop&w=1200&q=80"
                        alt="Am thuc da nang">
                    <div class="cuisine-highlight">
                        <span class="cuisine-highlight-badge">#</span>
                        <div>
                            <p class="cuisine-stat-label">Hơn</p>
                            <p class="cuisine-stat-value">1000+ món ăn</p>
                        </div>
                    </div>
                </article>

                <div class="cuisine-list">
                    @foreach ($dishes as $dish)
                        <article class="cuisine-card">
                            <div class="cuisine-card-top">
                                <h3 class="cuisine-dish-title">{{ $dish['name'] }}</h3>
                                <span class="cuisine-price">{{ $dish['price'] }}</span>
                            </div>
                            <p class="muted cuisine-dish-desc">{{ $dish['desc'] }}</p>
                        </article>
                    @endforeach
                </div>
            </div>
        </div>
    </section>
@endsection
