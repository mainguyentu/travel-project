@extends('layouts.admin')

@section('page-title', 'Dashboard')

@section('content')
    <div class="dashboard-container">
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
                                <td>{{ $item['favorite_count'] }}</td>
                            </tr>
                        @empty
                            <tr><td colspan="2">No data</td></tr>
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
                            <tr><td colspan="2">No data</td></tr>
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
                                <td>{{ $item['view_count'] }}</td>
                            </tr>
                        @empty
                            <tr><td colspan="2">No data</td></tr>
                        @endforelse
                    </tbody>
                </table>
            </section>
        </div>
    </div>
@endsection

@push('styles')
    <style>
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .kpi-card {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .kpi-value {
            font-size: 2rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 2rem;
        }

        .dashboard-section {
            background: white;
            padding: 1.5rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        .admin-table {
            width: 100%;
            border-collapse: collapse;
        }

        .admin-table th,
        .admin-table td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #eee;
        }

        .admin-table th {
            background: #f5f5f5;
            font-weight: bold;
        }
    </style>
@endpush
