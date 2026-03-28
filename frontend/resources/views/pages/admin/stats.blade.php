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

