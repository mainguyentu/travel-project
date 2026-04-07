@extends('layouts.admin')

@section('page-title', 'Dashboard')

@section('content')
    @php
        $totalUsers = (int) ($stats['total_users'] ?? 0);
        $totalDestinations = (int) ($stats['total_destinations'] ?? 0);
        $totalReviews = (int) ($stats['total_reviews'] ?? 0);
        $avgRating = (float) ($stats['avg_rating'] ?? 0);

        $favoriteItems = collect($stats['top_favorites'] ?? []);
        $ratingItems = collect($stats['top_ratings'] ?? []);
        $viewItems = collect($stats['top_views'] ?? []);

        $favoriteMax = max(1, (int) ($favoriteItems->max(fn ($item) => (int) ($item['favorite_count'] ?? 0)) ?? 0));
        $ratingMax = max(1, (int) ceil($ratingItems->max(fn ($item) => (float) ($item['rating_avg'] ?? 0)) ?? 0));
        $viewMax = max(1, (int) ($viewItems->max(fn ($item) => (int) ($item['view_count'] ?? 0)) ?? 0));
    @endphp

    <div class="dashboard-container admin-panel-shell dashboard-shell">
        <section class="dashboard-hero">
            <div class="dashboard-hero-copy">
                <span class="dashboard-eyebrow">Admin command center</span>
                <h2>Dashboard Overview</h2>
                <p>Theo dõi nhanh sức khỏe hệ thống, mức độ tương tác và các điểm đến đang được quan tâm.</p>

                <div class="dashboard-quick-links">
                    <a href="{{ route('admin.users.index') }}" class="dashboard-quick-link">Users</a>
                    <a href="{{ route('admin.categories.index') }}" class="dashboard-quick-link">Categories</a>
                    <a href="{{ route('admin.destinations.index') }}" class="dashboard-quick-link">Destinations</a>
                    <a href="{{ route('admin.stats.index') }}" class="dashboard-quick-link">Statistics</a>
                </div>
            </div>

            <div class="dashboard-hero-panel">
                <div class="dashboard-hero-metric">
                    <span>Average rating</span>
                    <strong>{{ number_format($avgRating, 1) }}</strong>
                </div>
                <div class="dashboard-hero-metric">
                    <span>Total users</span>
                    <strong>{{ number_format($totalUsers) }}</strong>
                </div>
                <div class="dashboard-hero-metric">
                    <span>Total destinations</span>
                    <strong>{{ number_format($totalDestinations) }}</strong>
                </div>
            </div>
        </section>

        @if (!empty($dashboardErrors))
            <div class="alert alert-danger" role="alert">
                <strong>Dashboard đang thiếu một phần dữ liệu:</strong>
                <ul>
                    @foreach ($dashboardErrors as $message)
                        <li>{{ $message }}</li>
                    @endforeach
                </ul>
            </div>
        @endif

        <div class="kpi-grid dashboard-kpi-grid">
            <div class="kpi-card dashboard-kpi-card dashboard-kpi-card-accent">
                <h3>Total Users</h3>
                <p class="kpi-value">{{ $totalUsers }}</p>
                <p class="kpi-note">Tài khoản đã đăng ký trên hệ thống.</p>
            </div>
            <div class="kpi-card dashboard-kpi-card">
                <h3>Total Destinations</h3>
                <p class="kpi-value">{{ $totalDestinations }}</p>
                <p class="kpi-note">Điểm đến đang được quản lý.</p>
            </div>
            <div class="kpi-card dashboard-kpi-card">
                <h3>Total Reviews</h3>
                <p class="kpi-value">{{ $totalReviews }}</p>
                <p class="kpi-note">Lượt phản hồi và đánh giá.</p>
            </div>
            <div class="kpi-card dashboard-kpi-card dashboard-kpi-card-soft">
                <h3>Avg Rating</h3>
                <p class="kpi-value">{{ number_format($avgRating, 1) }}</p>
                <p class="kpi-note">Điểm trung bình tổng hợp.</p>
            </div>
        </div>

        <div class="dashboard-main-grid">
            <section class="dashboard-section dashboard-leaderboard-card">
                <div class="section-header dashboard-section-header">
                    <div>
                        <span class="dashboard-section-kicker">Demand</span>
                        <h2>Most Viewed</h2>
                    </div>
                    <span class="dashboard-section-badge">{{ $viewItems->count() }} items</span>
                </div>

                <div class="dashboard-rank-list">
                    @forelse ($viewItems as $item)
                        @php
                            $viewCount = (int) ($item['view_count'] ?? 0);
                            $width = min(100, max(6, (int) round(($viewCount / $viewMax) * 100)));
                        @endphp
                        <article class="dashboard-rank-item">
                            <div class="dashboard-rank-top">
                                <div>
                                    <h3>{{ $item['name'] }}</h3>
                                    <p class="muted">Destination views</p>
                                </div>
                                <strong>{{ $viewCount }}</strong>
                            </div>
                            <div class="dashboard-bar" aria-hidden="true">
                                <span style="width: {{ $width }}%"></span>
                            </div>
                        </article>
                    @empty
                        <p class="dashboard-empty-state">Chưa có dữ liệu lượt xem.</p>
                    @endforelse
                </div>
            </section>

            <div class="dashboard-side-stack">
                <section class="dashboard-section dashboard-mini-card">
                    <div class="section-header dashboard-section-header">
                        <div>
                            <span class="dashboard-section-kicker">Community</span>
                            <h2>Top Favorites</h2>
                        </div>
                        <span class="dashboard-section-badge">{{ $favoriteItems->count() }} items</span>
                    </div>

                    <div class="dashboard-rank-list">
                        @forelse ($favoriteItems as $item)
                            @php
                                $favoriteCount = (int) ($item['favorite_count'] ?? 0);
                                $width = min(100, max(6, (int) round(($favoriteCount / $favoriteMax) * 100)));
                            @endphp
                            <article class="dashboard-rank-item dashboard-rank-item-compact">
                                <div class="dashboard-rank-top">
                                    <div>
                                        <h3>{{ $item['name'] }}</h3>
                                        <p class="muted">Favorites</p>
                                    </div>
                                    <strong>{{ $favoriteCount }}</strong>
                                </div>
                                <div class="dashboard-bar dashboard-bar-soft" aria-hidden="true">
                                    <span style="width: {{ $width }}%"></span>
                                </div>
                            </article>
                        @empty
                            <p class="dashboard-empty-state">Chưa có dữ liệu yêu thích.</p>
                        @endforelse
                    </div>
                </section>

                <section class="dashboard-section dashboard-mini-card">
                    <div class="section-header dashboard-section-header">
                        <div>
                            <span class="dashboard-section-kicker">Quality</span>
                            <h2>Top Rated</h2>
                        </div>
                        <span class="dashboard-section-badge">{{ $ratingItems->count() }} items</span>
                    </div>

                    <div class="dashboard-rank-list">
                        @forelse ($ratingItems as $item)
                            @php
                                $ratingScore = (float) ($item['rating_avg'] ?? 0);
                                $width = min(100, max(6, (int) round(($ratingScore / 5) * 100)));
                            @endphp
                            <article class="dashboard-rank-item dashboard-rank-item-compact">
                                <div class="dashboard-rank-top">
                                    <div>
                                        <h3>{{ $item['name'] }}</h3>
                                        <p class="muted">Avg rating</p>
                                    </div>
                                    <strong>{{ number_format($ratingScore, 1) }}/5</strong>
                                </div>
                                <div class="dashboard-bar dashboard-bar-warm" aria-hidden="true">
                                    <span style="width: {{ $width }}%"></span>
                                </div>
                            </article>
                        @empty
                            <p class="dashboard-empty-state">Chưa có dữ liệu đánh giá.</p>
                        @endforelse
                    </div>
                </section>
            </div>
        </div>
    </div>
@endsection
