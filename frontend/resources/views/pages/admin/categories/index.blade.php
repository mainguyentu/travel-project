@extends('layouts.admin')

@section('page-title', 'Categories Management')

@section('content')
    <div class="admin-section">
        <div class="section-header">
            <h2>Categories Management</h2>
            <span class="muted">Danh sách chỉ đọc theo dữ liệu API.</span>
        </div>

        @if ($categoriesError)
            <div class="alert alert-danger" role="alert">{{ $categoriesError }}</div>
        @endif

        <table class="admin-table full-width">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Slug</th>
                    <th>Description</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                @forelse ($categories as $category)
                    <tr>
                        <td>{{ $category['id'] }}</td>
                        <td>{{ $category['name'] }}</td>
                        <td><code>{{ $category['slug'] }}</code></td>
                        <td>{{ Str::limit($category['description'] ?? '', 50) }}</td>
                        <td>
                            <span class="status active">Xem thông tin</span>
                        </td>
                    </tr>
                @empty
                    <tr><td colspan="5">Không có danh mục để hiển thị.</td></tr>
                @endforelse
            </tbody>
        </table>
    </div>
@endsection

