@extends('layouts.admin')

@section('page-title', 'Statistics')

@section('content')
    @php
        $requestCount = (int) ($stats['total_requests'] ?? 0);
        $uniqueUsers = (int) ($stats['unique_users'] ?? 0);
        $avgResponseTime = (float) ($stats['avg_response_time'] ?? 0);
        $errorRate = (float) ($stats['error_rate'] ?? 0);
    @endphp

    <div class="stats-container admin-panel-shell admin-page-shell">
        <section class="dashboard-hero admin-page-hero">
            <div class="dashboard-hero-copy">
                <span class="dashboard-eyebrow">Operational metrics</span>
                <h2>Statistics Center</h2>
                <p>Bảng điều khiển dành cho theo dõi vận hành: phản hồi API, mức độ người dùng và tình trạng lỗi.</p>
            </div>

            <div class="dashboard-hero-panel">
                <div class="dashboard-hero-metric">
                    <span>Total requests</span>
                    <strong>{{ number_format($requestCount) }}</strong>
                </div>
                <div class="dashboard-hero-metric">
                    <span>Unique users</span>
                    <strong>{{ number_format($uniqueUsers) }}</strong>
                </div>
                <div class="dashboard-hero-metric">
                    <span>Error rate</span>
                    <strong>{{ number_format($errorRate, 1) }}%</strong>
                </div>
            </div>
        </section>

        @if (!empty($statsErrors))
            <div class="alert alert-danger" role="alert">
                <strong>Không thể tải đầy đủ dữ liệu thống kê:</strong>
                <ul>
                    @foreach ($statsErrors as $message)
                        <li>{{ $message }}</li>
                    @endforeach
                </ul>
            </div>
        @endif

        <section class="stats-section">
            <div class="section-header dashboard-section-header">
                <div>
                    <span class="dashboard-section-kicker">Request flow</span>
                    <h2>Request Statistics</h2>
                </div>
            </div>

            <div class="stats-grid dashboard-stats-grid">
                <div class="stat-card dashboard-stat-card">
                    <h3>Total Requests</h3>
                    <p class="stat-value">{{ $requestCount }}</p>
                </div>
                <div class="stat-card dashboard-stat-card">
                    <h3>Unique Users</h3>
                    <p class="stat-value">{{ $uniqueUsers }}</p>
                </div>
                <div class="stat-card dashboard-stat-card dashboard-stat-card-muted">
                    <h3>Avg Response Time</h3>
                    <p class="stat-value">{{ number_format($avgResponseTime, 0) }}ms</p>
                </div>
                <div class="stat-card dashboard-stat-card dashboard-stat-card-warn">
                    <h3>Error Rate</h3>
                    <p class="stat-value">{{ number_format($errorRate, 1) }}%</p>
                </div>
            </div>
        </section>

        <section class="stats-section">
            <div class="section-header dashboard-section-header">
                <div>
                    <span class="dashboard-section-kicker">Daily snapshot</span>
                    <h2>Activity Summary</h2>
                </div>
            </div>

            <div class="admin-table-wrap stats-summary-wrap">
                <table class="admin-table full-width stats-summary-table">
                    <thead>
                        <tr>
                            <th>Metric</th>
                            <th>Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>
                                <div class="dashboard-table-primary">
                                    <strong>New Users (Today)</strong>
                                    <span>Accounts created in the last 24 hours</span>
                                </div>
                            </td>
                            <td>{{ $stats['new_users_today'] ?? 0 }}</td>
                        </tr>
                        <tr>
                            <td>
                                <div class="dashboard-table-primary">
                                    <strong>New Reviews (Today)</strong>
                                    <span>Fresh social proof for destinations</span>
                                </div>
                            </td>
                            <td>{{ $stats['new_reviews_today'] ?? 0 }}</td>
                        </tr>
                        <tr>
                            <td>
                                <div class="dashboard-table-primary">
                                    <strong>Active Sessions</strong>
                                    <span>Live sessions currently tracked</span>
                                </div>
                            </td>
                            <td>{{ $stats['active_sessions'] ?? 0 }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>
    </div>
@endsection

