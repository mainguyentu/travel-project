@extends('layouts.admin')

@section('page-title', 'Users Management')

@section('content')
    <div class="admin-section">
        <div class="section-header">
            <h2>Users Management</h2>
            <a href="#" class="btn-primary">Add User</a>
        </div>

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
                            <div class="actions">
                                <a href="#" class="btn-small">Edit</a>
                                <button class="btn-small btn-danger" data-user-id="{{ $user['id'] }}">Delete</button>
                            </div>
                        </td>
                    </tr>
                @empty
                    <tr><td colspan="6">No users found</td></tr>
                @endforelse
            </tbody>
        </table>
    </div>
@endsection

@push('styles')
    <style>
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .full-width {
            width: 100%;
        }

        .badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: #e3f2fd;
            color: #1976d2;
            border-radius: 20px;
            font-size: 0.875rem;
        }

        .status {
            padding: 0.25rem 0.75rem;
            border-radius: 4px;
            font-size: 0.875rem;
        }

        .status.active {
            background: #c8e6c9;
            color: #1b5e20;
        }

        .status.inactive {
            background: #ffcdd2;
            color: #b71c1c;
        }

        .actions {
            display: flex;
            gap: 0.5rem;
        }

        .btn-small {
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
        }
    </style>
@endpush
