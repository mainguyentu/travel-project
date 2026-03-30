<aside class="admin-sidebar" aria-label="Sidebar quản trị">
    <div class="sidebar-header">
        <h2 class="sidebar-title">Admin Panel</h2>
    </div>

    <nav class="sidebar-nav" aria-label="Điều hướng quản trị">
        <a href="{{ route('admin.dashboard') }}" class="nav-item @if(request()->routeIs('admin.dashboard')) active @endif">
            📊 Dashboard
        </a>

        <a href="{{ route('admin.users.index') }}" class="nav-item @if(request()->routeIs('admin.users.*')) active @endif">
            👥 Quản Lý User
        </a>

        <a href="{{ route('admin.categories.index') }}" class="nav-item @if(request()->routeIs('admin.categories.*')) active @endif">
            🏷️ Quản Lý Category
        </a>

        <a href="{{ route('admin.destinations.index') }}" class="nav-item @if(request()->routeIs('admin.destinations.*')) active @endif">
            📍 Quản Lý Destination
        </a>

        <a href="{{ route('admin.stats.index') }}" class="nav-item @if(request()->routeIs('admin.stats.*')) active @endif">
            📈 Thống Kê
        </a>
    </nav>

    <div class="sidebar-footer">
        <a href="{{ route('home') }}" class="sidebar-link-text">← Quay lại trang web</a>
    </div>
</aside>

