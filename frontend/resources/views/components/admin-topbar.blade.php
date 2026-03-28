<div class="admin-topbar">
    <div class="topbar-left">
        <span class="page-title">@yield('page_title', 'Dashboard')</span>
    </div>

    <div class="topbar-right">
        <div class="user-info">
            <span class="user-name">{{ auth()->user()->name }}</span>
            <form method="POST" action="{{ route('logout') }}" class="d-inline">
                @csrf
                <button type="submit" class="logout-btn">Đăng Xuất</button>
            </form>
        </div>
    </div>
</div>

