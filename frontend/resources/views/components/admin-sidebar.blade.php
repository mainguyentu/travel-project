<aside class="admin-sidebar">
    <div class="sidebar-header">
        <h2 class="sidebar-title">Admin Panel</h2>
    </div>

    <nav class="sidebar-nav">
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
        <a href="{{ route('home') }}" class="sidebar-link-text">← Quay Lại Frontend</a>
    </div>
</aside>

<style>
    .admin-sidebar {
        width: 250px;
        background-color: #2c3e50;
        color: #fff;
        padding: 2rem 0;
        height: 100vh;
        overflow-y: auto;
        position: sticky;
        top: 0;
    }

    .sidebar-header {
        padding: 0 1.5rem;
        margin-bottom: 2rem;
    }

    .sidebar-title {
        margin: 0;
        font-size: 1.25rem;
        color: #0066cc;
    }

    .sidebar-nav {
        display: flex;
        flex-direction: column;
        gap: 0;
    }

    .nav-item {
        display: block;
        padding: 1rem 1.5rem;
        color: #ecf0f1;
        text-decoration: none;
        transition: background-color 0.3s, color 0.3s;
        border-left: 4px solid transparent;
    }

    .nav-item:hover {
        background-color: #34495e;
        color: #0066cc;
    }

    .nav-item.active {
        background-color: #0066cc;
        color: #fff;
        border-left-color: #00ccff;
    }

    .sidebar-footer {
        position: absolute;
        bottom: 1rem;
        left: 0;
        right: 0;
        padding: 0 1.5rem;
    }

    .sidebar-link-text {
        color: #95a5a6;
        text-decoration: none;
        font-size: 0.9rem;
    }

    .sidebar-link-text:hover {
        color: #0066cc;
    }
</style>
