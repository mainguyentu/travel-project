<header class="site-header">
    <div class="header-inner">
        <a href="{{ route('home') }}" class="brand">
            <span class="brand-logo">Đ</span>
            <span>
                <span class="brand-name">Đà Nẵng</span><br>
                <span class="brand-sub">Atlas Du lịch</span>
            </span>
        </a>
        <nav class="nav-desktop">
            <a href="{{ route('home') }}">Trang chủ</a>
            <a href="{{ route('destinations.index') }}">Điểm đến</a>
            @if (session('access_token'))
                <a href="{{ route('favorites.index') }}">Yêu thích</a>
                <a href="{{ route('profile.index') }}">Hồ sơ</a>
                @if (session('is_admin'))
                    <a href="{{ route('admin.dashboard') }}">Admin</a>
                @endif
                <form method="POST" action="{{ route('logout') }}" class="inline-form">
                    @csrf
                    <button type="submit" class="btn btn-ghost">Đăng xuất</button>
                </form>
            @else
                <a href="{{ route('login') }}">Đăng nhập</a>
                <a href="{{ route('register') }}" class="btn">Đăng ký</a>
            @endif
            <button type="button" class="theme-toggle" aria-label="Đổi giao diện" onclick="toggleTheme()">◐</button>
        </nav>
        <button class="nav-toggle" type="button" aria-label="Menu" onclick="document.querySelector('.nav-mobile').classList.toggle('open')">☰</button>
    </div>
    <nav class="nav-mobile">
        <a href="{{ route('home') }}">Trang chủ</a>
        <a href="{{ route('destinations.index') }}">Điểm đến</a>
        @if (session('access_token'))
            <a href="{{ route('favorites.index') }}">Yêu thích</a>
            <a href="{{ route('profile.index') }}">Hồ sơ</a>
            @if (session('is_admin'))
                <a href="{{ route('admin.dashboard') }}">Admin</a>
            @endif
        @else
            <a href="{{ route('login') }}">Đăng nhập</a>
            <a href="{{ route('register') }}">Đăng ký</a>
        @endif
    </nav>
</header>
