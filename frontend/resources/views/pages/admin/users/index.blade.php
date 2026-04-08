@extends('layouts.admin')

@section('page-title', 'Users Management')

@section('content')
    @php
        $userCount = collect($users ?? [])->count();
        $adminCount = collect($users ?? [])->filter(fn ($user) => ($user['role'] ?? 'user') === 'admin')->count();
        $lockedCount = collect($users ?? [])->filter(fn ($user) => ($user['status'] ?? 'active') === 'locked')->count();
    @endphp

    <div class="admin-panel-shell admin-page-shell">
        <section class="dashboard-hero admin-page-hero">
            <div class="dashboard-hero-copy">
                <span class="dashboard-eyebrow">Access control</span>
                <h2>Users Management</h2>
                <p>Điều phối trạng thái và vai trò người dùng từ một control surface gọn, rõ và đủ lực.</p>

                <div class="dashboard-quick-links">
                    <a href="#users-table" class="dashboard-quick-link">Xem danh sách</a>
                </div>
            </div>

            <div class="dashboard-hero-panel">
                <div class="dashboard-hero-metric">
                    <span>Total users</span>
                    <strong>{{ $userCount }}</strong>
                </div>
                <div class="dashboard-hero-metric">
                    <span>Admins</span>
                    <strong>{{ $adminCount }}</strong>
                </div>
                <div class="dashboard-hero-metric">
                    <span>Locked accounts</span>
                    <strong>{{ $lockedCount }}</strong>
                </div>
            </div>
        </section>

        @if ($usersError)
            <div class="alert alert-danger" role="alert">{{ $usersError }}</div>
        @endif

        <div class="admin-table-wrap" id="users-table">
            <table class="admin-table full-width">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Role</th>
                        <th>Status</th>
                        <th class="col-actions">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse ($users as $user)
                        <tr>
                            <td>{{ $user['id'] }}</td>
                            <td>
                                <div class="dashboard-table-primary">
                                    <strong>{{ $user['name'] }}</strong>
                                    <span>{{ $user['role'] === 'admin' ? 'Administrator access' : 'Standard member' }}</span>
                                </div>
                            </td>
                            <td>{{ $user['email'] }}</td>
                            <td>
                                <span class="badge">{{ ucfirst($user['role'] ?? 'user') }}</span>
                            </td>
                            <td>
                                <span class="status {{ ($user['status'] ?? 'active') === 'active' ? 'active' : 'inactive' }}">
                                    {{ ucfirst($user['status'] ?? 'active') }}
                                </span>
                            </td>
                            <td class="table-actions-cell">
                                <div class="actions dashboard-actions-stack">
                                    <form method="POST" action="{{ route('admin.users.status', $user['id']) }}" class="admin-inline-action">
                                        @csrf
                                        @method('PATCH')
                                        <select name="status" class="form-control">
                                            <option value="active" @selected(($user['status'] ?? 'active') === 'active')>Active</option>
                                            <option value="locked" @selected(($user['status'] ?? 'active') === 'locked')>Locked</option>
                                        </select>
                                        <button type="submit" class="btn-small">Cập nhật</button>
                                    </form>
                                    <form method="POST" action="{{ route('admin.users.role', $user['id']) }}" class="admin-inline-action">
                                        @csrf
                                        @method('PATCH')
                                        <select name="role" class="form-control">
                                            <option value="user" @selected(($user['role'] ?? 'user') === 'user')>User</option>
                                            <option value="admin" @selected(($user['role'] ?? 'user') === 'admin')>Admin</option>
                                        </select>
                                        <button type="submit" class="btn-small">Cập nhật</button>
                                    </form>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="6">Không có người dùng để hiển thị.</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>
@endsection

