@extends('layouts.admin')

@section('title', 'Quản lý users')

@section('content')
<div class="page-head"><div><h1>Users</h1><p class="muted">Tổng {{ $meta['total'] ?? 0 }}</p></div></div>
<table class="admin-table">
    <thead><tr><th>ID</th><th>Tên</th><th>Email</th><th>Role</th><th>Status</th><th>Hành động</th></tr></thead>
    <tbody>
    @foreach ($users as $u)
        <tr>
            <td>{{ $u['id'] }}</td>
            <td>{{ $u['name'] }}</td>
            <td>{{ $u['email'] }}</td>
            <td><span class="badge {{ $u['role'] === 'admin' ? 'badge-admin' : 'badge-user' }}">{{ $u['role'] }}</span></td>
            <td><span class="badge {{ $u['status'] === 'active' ? 'badge-ok' : 'badge-locked' }}">{{ $u['status'] === 'active' ? '✓ active' : '🔒 locked' }}</span></td>
            <td>
                <form method="POST" action="{{ route('admin.users.status', ['id' => $u['id']]) }}" class="inline-form">
                    @csrf @method('PATCH')
                    <select name="status">
                        <option value="active" @selected($u['status'] === 'active')>active</option>
                        <option value="locked" @selected($u['status'] === 'locked')>locked</option>
                    </select>
                    <button type="submit" class="btn-small">Lưu</button>
                </form>
                <form method="POST" action="{{ route('admin.users.role', ['id' => $u['id']]) }}" class="inline-form">
                    @csrf @method('PATCH')
                    <select name="role">
                        <option value="user" @selected($u['role'] === 'user')>user</option>
                        <option value="admin" @selected($u['role'] === 'admin')>admin</option>
                    </select>
                    <button type="submit" class="btn-small">Lưu</button>
                </form>
            </td>
        </tr>
    @endforeach
    </tbody>
</table>
@endsection
