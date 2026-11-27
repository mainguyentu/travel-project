<header class="topbar">
    <a href="{{ route('admin.dashboard') }}" class="brand-mini">Admin — Alats Travel</a>
    <div class="topbar-actions">
        <a href="{{ route('home') }}">Xem site</a>
        <button type="button" class="theme-toggle" aria-label="Đổi giao diện" onclick="toggleTheme()">◐</button>
        <form method="POST" action="{{ route('logout') }}" class="inline-form">
            @csrf
            <button type="submit" class="btn-small">Đăng xuất</button>
        </form>
    </div>
</header>
