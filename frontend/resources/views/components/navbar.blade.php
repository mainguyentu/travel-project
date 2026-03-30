@php
    $sessionUser = session('user');
    $isAuthenticated = session()->has('access_token') && $sessionUser;
    $isAdmin =
        is_array($sessionUser) && (($sessionUser['role'] ?? '') === 'admin' || ($sessionUser['is_admin'] ?? false));
@endphp

<nav class="site-nav" aria-label="Điều hướng chính">
    <div class="site-container">
        <div class="site-nav-inner">
            <a href="{{ route('home') }}" class="brand" aria-label="Alats Travel">
                <span class="brand-mark">✦</span>
                <span>
                    <p class="brand-title">Alats Travel</p>
                    <p class="brand-subtitle">Atlas du lịch Đà Nẵng</p>
                </span>
            </a>

            <ul class="site-nav-links" role="list">
                <li><a href="{{ route('home') }}">Trang chủ</a></li>
                <li><a href="{{ route('destinations.index') }}">Điểm đến</a></li>
                <li><a href="{{ route('favorites.index') }}">Yêu thích</a></li>
                <li><a href="{{ route('profile.index') }}">Hồ sơ</a></li>
            </ul>

            <div class="site-nav-actions">
                @if ($isAuthenticated)
                    <div class="user-menu" data-user-menu>
                        <button
                            class="user-menu-btn"
                            type="button"
                            data-user-menu-toggle
                            aria-expanded="false"
                            aria-controls="user-menu-list"
                            aria-haspopup="menu">
                            {{ $sessionUser['name'] ?? 'Tai khoan' }}
                        </button>
                        <div class="user-menu-list" id="user-menu-list" data-user-menu-list role="menu">
                            <a href="{{ route('profile.index') }}" role="menuitem">Hồ sơ</a>
                            <a href="{{ route('favorites.index') }}" role="menuitem">Yêu thích</a>
                            @if ($isAdmin)
                                <hr>
                                <a href="{{ route('admin.dashboard') }}" role="menuitem">Dashboard Admin</a>
                            @endif
                            <hr>
                            <form method="POST" action="{{ route('logout') }}">
                                @csrf
                                <button type="submit" role="menuitem">Đăng xuất</button>
                            </form>
                        </div>
                    </div>
                @else
                    <a href="{{ route('login') }}" class="btn-primary">Đăng nhập</a>
                    <a href="{{ route('register') }}" class="btn-outline">Đăng ký</a>
                @endif
            </div>

            <button
                class="mobile-nav-toggle"
                type="button"
                aria-label="Mở menu điều hướng"
                aria-expanded="false"
                aria-controls="mobile-nav"
                data-mobile-toggle>
                ☰
            </button>
        </div>

        <div class="mobile-nav" id="mobile-nav" data-mobile-nav hidden>
            <a href="{{ route('home') }}">Trang chủ</a>
            <a href="{{ route('destinations.index') }}">Điểm đến</a>
            @if ($isAuthenticated)
                <a href="{{ route('favorites.index') }}">Yêu thích</a>
                <a href="{{ route('profile.index') }}">Hồ sơ</a>
                @if ($isAdmin)
                    <a href="{{ route('admin.dashboard') }}">Dashboard Admin</a>
                @endif
                <form method="POST" action="{{ route('logout') }}">
                    @csrf
                    <button type="submit" class="btn-secondary btn-block">Đăng xuất</button>
                </form>
            @else
                <a href="{{ route('login') }}">Đăng nhập</a>
                <a href="{{ route('register') }}">Đăng ký</a>
            @endif
        </div>
    </div>
</nav>

