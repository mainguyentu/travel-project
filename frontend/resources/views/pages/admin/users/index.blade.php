@extends('layouts.admin')

@section('page-title', 'Users Management')

@section('content')
    <div class="admin-section">
        <div class="section-header">
            <h2>Users Management</h2>
            <span class="muted">Danh sách chỉ đọc theo dữ liệu API.</span>
        </div>

        @if ($usersError)
            <div class="alert alert-danger" role="alert">{{ $usersError }}</div>
        @endif

        <table class="admin-table full-width">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                @forelse ($users as $user)
                    <tr>
                        <td>{{ $user['id'] }}</td>
                        <td>{{ $user['name'] }}</td>
                        <td>{{ $user['email'] }}</td>
                        <td>
                            <span class="badge">{{ ucfirst($user['role'] ?? 'user') }}</span>
                        </td>
                        <td>
                            <span class="status {{ ($user['status'] ?? 'active') === 'active' ? 'active' : 'inactive' }}">
                                {{ ucfirst($user['status'] ?? 'active') }}
                            </span>
                        </td>
                        <td>
                            <span class="status active">Xem thông tin</span>
                        </td>
                    </tr>
                @empty
                    <tr><td colspan="6">Không có người dùng để hiển thị.</td></tr>
                @endforelse
            </tbody>
        </table>
    </div>
@endsection

