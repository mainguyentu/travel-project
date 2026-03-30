@php
    $sessionUser = session('user');
@endphp

<div class="admin-topbar">
    <div class="topbar-left">
        <span class="page-title">@yield('page-title', 'Dashboard')</span>
    </div>

    <div class="topbar-right">
        <div class="user-info">
            <span class="user-name">{{ $sessionUser['name'] ?? 'Tai khoan' }}</span>
            <form method="POST" action="{{ route('logout') }}" class="d-inline">
                @csrf
                <button type="submit" class="logout-btn" aria-label="Đăng xuất tài khoản">Đăng xuất</button>
            </form>
        </div>
    </div>
</div>

