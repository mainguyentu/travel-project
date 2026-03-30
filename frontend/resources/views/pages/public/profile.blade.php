@extends('layouts.app')

@section('title', 'My Profile - Alats Travel')

@section('content')
    <section class="public-shell">
        <div class="site-container">
            <header class="public-page-header">
                <h1>Hồ sơ của tôi</h1>
                <p>Quản lý thông tin tài khoản của bạn.</p>
            </header>

            @if (session('success'))
                <div class="alert alert-success" role="status">{{ session('success') }}</div>
            @endif

            @if ($errors->any())
                <div class="alert alert-error" role="alert">
                    <ul>
                        @foreach ($errors->all() as $error)
                            <li>{{ $error }}</li>
                        @endforeach
                    </ul>
                </div>
            @endif

            <div class="profile-grid">
                <section class="profile-panel panel">
                    <h2 class="profile-panel-title">Thông tin tài khoản</h2>

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
                    <h2 class="profile-panel-title">Tác vụ nhanh</h2>
                    <div class="profile-quick-actions">
                        <a href="{{ route('favorites.index') }}" class="btn-secondary">Xem danh sách yêu thích</a>
                        <a href="{{ route('destinations.index') }}" class="btn-secondary">Khám phá điểm đến</a>
                        <p class="muted">Cập nhật hồ sơ sẽ được mở ở phiên bản kế tiếp.</p>
                    </div>
                </section>
            </div>
        </div>
    </section>
@endsection
