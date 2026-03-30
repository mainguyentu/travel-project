@extends('layouts.admin')

@section('page-title', 'Dashboard')

@section('content')
    <div class="dashboard-container">
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

        <!-- KPI Cards -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <h3>Total Users</h3>
                <p class="kpi-value">{{ $stats['total_users'] ?? 0 }}</p>
            </div>
            <div class="kpi-card">
                <h3>Total Destinations</h3>
                <p class="kpi-value">{{ $stats['total_destinations'] ?? 0 }}</p>
            </div>
            <div class="kpi-card">
                <h3>Total Reviews</h3>
                <p class="kpi-value">{{ $stats['total_reviews'] ?? 0 }}</p>
            </div>
            <div class="kpi-card">
                <h3>Avg Rating</h3>
                <p class="kpi-value">{{ $stats['avg_rating'] ?? 0 }}</p>
            </div>
        </div>

        <!-- Top Tables -->
        <div class="dashboard-grid">
            <!-- Top Favorites -->
            <section class="dashboard-section">
                <h2>Top Favorites</h2>
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>Destination</th>
                            <th>Favorites</th>
                        </tr>
                    </thead>
                    <tbody>
                        @forelse ($stats['top_favorites'] ?? [] as $item)
                            <tr>
                                <td>{{ $item['name'] }}</td>
                                <td>{{ $item['favorite_count'] ?? 0 }}</td>
                            </tr>
                        @empty
                            <tr><td colspan="2">Chưa có dữ liệu yêu thích.</td></tr>
                        @endforelse
                    </tbody>
                </table>
            </section>

            <!-- Top Ratings -->
            <section class="dashboard-section">
                <h2>Top Rated</h2>
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>Destination</th>
                            <th>Rating</th>
                        </tr>
                    </thead>
                    <tbody>
                        @forelse ($stats['top_ratings'] ?? [] as $item)
                            <tr>
                                <td>{{ $item['name'] }}</td>
                                <td>{{ $item['rating_avg'] }}/5</td>
                            </tr>
                        @empty
                            <tr><td colspan="2">Chưa có dữ liệu đánh giá.</td></tr>
                        @endforelse
                    </tbody>
                </table>
            </section>

            <!-- Most Views -->
            <section class="dashboard-section">
                <h2>Most Viewed</h2>
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th>Destination</th>
                            <th>Views</th>
                        </tr>
                    </thead>
                    <tbody>
                        @forelse ($stats['top_views'] ?? [] as $item)
                            <tr>
                                <td>{{ $item['name'] }}</td>
                                <td>{{ $item['view_count'] ?? 0 }}</td>
                            </tr>
                        @empty
                            <tr><td colspan="2">Chưa có dữ liệu lượt xem.</td></tr>
                        @endforelse
                    </tbody>
                </table>
            </section>
        </div>
    </div>
@endsection

