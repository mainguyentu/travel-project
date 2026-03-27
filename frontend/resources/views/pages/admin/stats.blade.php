@extends('layouts.admin')

@section('page-title', 'Statistics')

@section('content')
    <div class="stats-container">
        <!-- Request Statistics -->
        <section class="stats-section">
            <h2>Request Statistics</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total Requests</h3>
                    <p class="stat-value">{{ $stats['total_requests'] ?? 0 }}</p>
                </div>
                <div class="stat-card">
                    <h3>Unique Users</h3>
                    <p class="stat-value">{{ $stats['unique_users'] ?? 0 }}</p>
                </div>
                <div class="stat-card">
                    <h3>Avg Response Time</h3>
                    <p class="stat-value">{{ $stats['avg_response_time'] ?? 0 }}ms</p>
                </div>
                <div class="stat-card">
                    <h3>Error Rate</h3>
                    <p class="stat-value">{{ $stats['error_rate'] ?? 0 }}%</p>
                </div>
            </div>
        </section>

        <!-- Activity Summary -->
        <section class="stats-section">
            <h2>Activity Summary</h2>
            <table class="admin-table full-width">
                <thead>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>New Users (Today)</td>
                        <td>{{ $stats['new_users_today'] ?? 0 }}</td>
                    </tr>
                    <tr>
                        <td>New Reviews (Today)</td>
                        <td>{{ $stats['new_reviews_today'] ?? 0 }}</td>
                    </tr>
                    <tr>
                        <td>Active Sessions</td>
                        <td>{{ $stats['active_sessions'] ?? 0 }}</td>
                    </tr>
                </tbody>
            </table>
        </section>
    </div>
@endsection

@push('styles')
    <style>
        .stats-container {
            max-width: 1200px;
        }

        .stats-section {
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }

        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
        }

        .stat-card:nth-child(2) {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        .stat-card:nth-child(3) {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        .stat-card:nth-child(4) {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            margin: 0.5rem 0;
        }

        .full-width {
            width: 100%;
        }
    </style>
@endpush
