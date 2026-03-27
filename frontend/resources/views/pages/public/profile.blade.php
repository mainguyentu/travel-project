@extends('layouts.app')

@section('title', 'My Profile - Alats Travel')

@section('content')
    <section class="public-shell">
        <div class="site-container">
            <header class="public-page-header">
                <h1>Hồ sơ của tôi</h1>
                <p>Quản lý thông tin tài khoản và điều hướng nhanh đến các tính năng quan trọng.</p>
            </header>

            <div class="profile-grid">
                <section class="profile-panel panel">
                    <h2 style="margin-top:0;">Thông tin tài khoản</h2>

                    <div class="profile-item">
                        <strong>Họ tên</strong>
                        <span>{{ $user['name'] ?? 'N/A' }}</span>
                    </div>
                    <div class="profile-item">
                        <strong>Email</strong>
                        <span>{{ $user['email'] ?? 'N/A' }}</span>
                    </div>
                    <div class="profile-item">
                        <strong>ngày tham gia</strong>
                        <span>{{ $user['created_at'] ?? 'N/A' }}</span>
                    </div>
                </section>

                <section class="profile-panel panel">
                    <h2 style="margin-top:0;">Tác vụ nhanh</h2>
                    <div style="display:grid; gap:0.65rem; margin-top:0.9rem;">
                        <a href="{{ route('favorites.index') }}" class="btn-secondary">Xem danh sách yêu thích</a>
                        <a href="{{ route('destinations.index') }}" class="btn-secondary">Khám phá điểm đến</a>
                    </div>
                </section>
            </div>
        </div>
    </section>
@endsection
