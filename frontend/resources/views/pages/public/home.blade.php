@extends('layouts.app')

@section('title', 'Home')

@section('content')
    <section class="home-hero" id="home">
        <div class="site-container home-hero-content">
            <h1>
                Khám phá <span class="text-gradient">Đà Nẵng</span>
            </h1>
            <p>
                Thành phố đáng sống nhất Việt Nam - Nơi biển xanh hòa quyện với núi non hùng vĩ
            </p>

            <form action="{{ route('destinations.index') }}" method="GET" class="hero-search" role="search">
                <div class="hero-search-field">
                    <svg class="hero-search-icon" viewBox="0 0 24 24" aria-hidden="true">
                        <path d="M11 19a8 8 0 1 1 0-16 8 8 0 0 1 0 16Zm10 2-4.35-4.35" fill="none" stroke="currentColor"
                            stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    <input type="text" name="search" placeholder="Tìm điểm đến, hoạt động, ẩm thực...">
                </div>
                <button type="submit" class="btn-primary">Tìm kiếm</button>
            </form>

            <div class="hero-quick-links">
                <a href="{{ route('destinations.index') }}" class="btn-ghost">Xem tất cả điểm đến</a>
                <a href="{{ route('destinations.index', ['rating' => 4.5]) }}" class="btn-ghost">Top đánh giá</a>
            </div>
        </div>
        <span class="hero-scroll" aria-hidden="true"></span>
    </section>


    @if ($homeError)
        <section class="section-pad">
            <div class="site-container">
                <div class="alert alert-error" role="alert">
                    <strong>Không thể tải đầy đủ dữ liệu trang chủ.</strong>
                    <p>{{ $homeError }} Bạn vẫn có thể tiếp tục khám phá danh sách điểm đến.</p>
                    <a href="{{ route('destinations.index') }}" class="btn-secondary">Mở danh sách điểm đến</a>
                </div>
            </div>
        </section>
    @endif

    <section class="section-pad section-soft-cyan" id="destinations">
        <div class="site-container">
            <div class="section-heading">
                <h2>Điểm đến <span class="text-gradient">nổi bật</span></h2>
                <p>
                    Khám phá những điểm đến đang được yêu thích nhất tại Đà Nẵng.
                </p>
            </div>

            <div class="destination-grid">
                @forelse ($destinations as $destination)
                    @include('components.destination-card', ['destination' => $destination])
                @empty
                    @if (!$homeError)
                        <div class="card-skeleton-grid" aria-hidden="true">
                            <div class="card-skeleton"></div>
                            <div class="card-skeleton"></div>
                            <div class="card-skeleton"></div>
                        </div>
                    @endif

                    <div class="empty-state">
                        <p>Chưa có địa điểm nổi bật.</p>
                    </div>
                @endforelse
            </div>

            @component('components.destination-detail-modal', ['destinations' => $destinations])
            @endcomponent
        </div>
    </section>

    {{-- <section class="section-pad" id="activities">
        <div class="site-container">
            <div class="section-heading">
                <h2>Hoạt động <span class="text-gradient">du lịch</span></h2>
                <p>Gợi ý theo {{ $selectedActivityName }}</p>
            </div>

            @if (!$activityRecommendationFeatureEnabled)
                <div class="alert alert-info" role="status">
                    <strong>Tính năng gợi ý hoạt động đang được triển khai.</strong>
                    <p>
                        Endpoint: {{ $activityRecommendationEndpointEnabled ? 'ON' : 'OFF' }} |
                        Home integration: {{ $activityRecommendationHomeEnabled ? 'ON' : 'OFF' }}
                    </p>
                </div>
            @else

            <div class="activity-switcher" aria-label="Chọn nhóm hoạt động">
                @foreach ($activityTabs as $slug => $activity)
                    <a
                        href="{{ route('home', ['activity_slug' => $slug]) }}"
                        class="{{ $selectedActivitySlug === $slug ? 'btn-primary' : 'btn-ghost' }}">
                        {{ $activity['name'] }}
                    </a>
                @endforeach
            </div>

            @if ($activityRecommendationError)
                <div class="alert alert-error activity-error-card" role="alert">
                    <strong>Lỗi API Endpoint {{ $activityRecommendationError['code'] }}</strong>
                    <p>{{ $activityRecommendationError['message'] }}</p>
                </div>
            @endif

            <div class="activity-recommendation-stack">
                @php
                    $activityBlocks = [
                        [
                            'key' => 'highlight_destinations',
                            'title' => 'Điểm nổi bật',
                            'description' => 'Top lựa chọn phù hợp nhất cho hoạt động đang xem.',
                            'empty' => 'Chưa có điểm nổi bật cho hoạt động này.',
                        ],
                        [
                            'key' => 'recommended_destinations',
                            'title' => 'Gợi ý thêm',
                            'description' => 'Các điểm đến tiếp theo để khám phá theo cùng sở thích.',
                            'empty' => 'Chưa có gợi ý bổ sung.',
                        ],
                        [
                            'key' => 'trending',
                            'title' => 'Xu hướng',
                            'description' => 'Những điểm đến đang được quan tâm nhiều nhất.',
                            'empty' => 'Chưa có dữ liệu xu hướng.',
                        ],
                    ];
                @endphp

                @foreach ($activityBlocks as $activityBlock)
                    <section class="activity-panel">
                        <div class="activity-panel-head">
                            <div>
                                <h3>{{ $activityBlock['title'] }}</h3>
                                <p class="muted">{{ $activityBlock['description'] }}</p>
                            </div>
                        </div>

                        <div class="destination-grid">
                            @forelse (($activityRecommendations[$activityBlock['key']] ?? []) as $destination)
                                @include('components.destination-card', ['destination' => $destination])
                            @empty
                                <div class="empty-state">
                                    <p>{{ $activityBlock['empty'] }}</p>
                                </div>
                            @endforelse
                        </div>
                    </section>
                @endforeach
            </div>
            @endif
        </div>
    </section> --}}

    <section class="section-pad section-soft-cyan" id="cuisine">
        <div class="site-container">
            <div class="section-heading">
                <h2>Ẩm thực <span class="text-gradient">Đà Nẵng</span></h2>
                <p>Khám phá hương vị đặc trưng của ẩm thực miền Trung Việt Nam</p>
            </div>

            @php
                $dishes = [
                    [
                        'name' => 'Mì Quảng',
                        'price' => '30.000 - 50.000đ',
                        'desc' => 'Món mì truyền thống đặc trưng của miền Trung với nước dùng đậm đà.',
                    ],
                    [
                        'name' => 'Bún chả cá',
                        'price' => '35.000 - 60.000đ',
                        'desc' => 'Bún tươi kết hợp với chả cá thơm ngon, đặc sản Đà Nẵng.',
                    ],
                    [
                        'name' => 'Bánh tráng cuốn thịt heo',
                        'price' => '40.000 - 70.000đ',
                        'desc' => 'Món ăn nhẹ nhàng, thanh mát với bánh tráng mỏng và thịt heo luộc.',
                    ],
                    [
                        'name' => 'Bê thui Cầu Mống',
                        'price' => '150.000 - 300.000đ',
                        'desc' => 'Thịt bê non thui thơm phức, món đặc sản nổi tiếng.',
                    ],
                    [
                        'name' => 'Hải sản tươi sống',
                        'price' => 'Theo thời giá',
                        'desc' => 'Hải sản tươi ngon được chế biến theo nhiều cách.',
                    ],
                    [
                        'name' => 'Bánh xèo',
                        'price' => '25.000 - 45.000đ',
                        'desc' => 'Bánh xèo giòn tan với nhân tôm, thịt, giá đỗ.',
                    ],
                ];
            @endphp

            <div class="cuisine-layout">
                <article class="cuisine-hero">
                    <img src="https://images.unsplash.com/photo-1696654351863-4d9a6d9cd4b9?auto=format&fit=crop&w=1200&q=80"
                        alt="Am thuc da nang">
                    <div class="cuisine-highlight">
                        <span class="cuisine-highlight-badge" aria-hidden="true">
                            <svg viewBox="0 0 24 24">
                                <path d="M7 10V7a5 5 0 0 1 10 0v3" fill="none" stroke="currentColor" stroke-width="2"
                                    stroke-linecap="round" stroke-linejoin="round" />
                                <path d="M5 10h14v7a3 3 0 0 1-3 3H8a3 3 0 0 1-3-3v-7Z" fill="none" stroke="currentColor"
                                    stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                                <path d="M9 15h6" fill="none" stroke="currentColor" stroke-width="2"
                                    stroke-linecap="round" stroke-linejoin="round" />
                            </svg>
                        </span>
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
