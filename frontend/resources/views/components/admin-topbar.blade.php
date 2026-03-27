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

<style>
    .admin-topbar {
        background-color: #fff;
        border-bottom: 1px solid #e5e5e5;
        padding: 1rem 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }

    .page-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #333;
    }

    .user-info {
        display: flex;
        gap: 1rem;
        align-items: center;
    }

    .user-name {
        color: #666;
        font-weight: 500;
    }

    .logout-btn {
        background: #d9534f;
        color: white;
        padding: 0.5rem 1rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        transition: background 0.3s;
    }

    .logout-btn:hover {
        background: #c9302c;
    }
</style>
