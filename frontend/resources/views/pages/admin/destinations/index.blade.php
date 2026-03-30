@extends('layouts.admin')

@section('page-title', 'Destinations Management')

@section('content')
    <div class="admin-section">
        <div class="section-header">
            <h2>Destinations Management</h2>
            <span class="muted">Danh sách chỉ đọc theo dữ liệu API.</span>
        </div>

        @if ($destinationsError)
            <div class="alert alert-danger" role="alert">{{ $destinationsError }}</div>
        @endif

        <table class="admin-table full-width">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Slug</th>
                    <th>Category</th>
                    <th>Rating</th>
                    <th>Views</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                @forelse ($destinations as $destination)
                    <tr>
                        <td>{{ $destination['id'] }}</td>
                        <td>{{ $destination['name'] }}</td>
                        <td><code>{{ $destination['slug'] }}</code></td>
                        <td>{{ $destination['categories'][0]['name'] ?? 'N/A' }}</td>
                        <td>
                            <span class="rating">
                                {{ $destination['rating_avg'] ?? 0 }}/5 ⭐
                            </span>
                        </td>
                        <td>{{ $destination['view_count'] ?? 0 }}</td>
                        <td>
                            <span class="muted">Xem nhanh tại danh sách public</span>
                        </td>
                    </tr>
                @empty
                    <tr><td colspan="7">Không có điểm đến để hiển thị.</td></tr>
                @endforelse
            </tbody>
        </table>
    </div>
@endsection

