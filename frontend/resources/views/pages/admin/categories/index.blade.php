@extends('layouts.admin')

@section('page-title', 'Categories Management')

@section('content')
    @php
        $categoryCount = collect($categories ?? [])->count();
        $categoryWithDescriptionCount = collect($categories ?? [])->filter(fn ($category) => !empty($category['descriptions']))->count();
    @endphp

    <div class="admin-panel-shell admin-page-shell">
        <section class="dashboard-hero admin-page-hero">
            <div class="dashboard-hero-copy">
                <span class="dashboard-eyebrow">Content structure</span>
                <h2>Categories Management</h2>
                <p>Quản lý nhóm danh mục cho hệ thống điểm đến.</p>

                <div class="dashboard-quick-links">
                    <a href="#category-table" class="dashboard-quick-link">Xem danh sách</a>
                    <a href="#category-create-section" class="dashboard-quick-link" data-open-target="#category-create-form">Tạo danh mục</a>
                </div>
            </div>

            <div class="dashboard-hero-panel">
                <div class="dashboard-hero-metric">
                    <span>Total categories</span>
                    <strong>{{ $categoryCount }}</strong>
                </div>
                <div class="dashboard-hero-metric">
                    <span>Has description</span>
                    <strong>{{ $categoryWithDescriptionCount }}</strong>
                </div>
                <div class="dashboard-hero-metric">
                    <span>Action mode</span>
                    <strong>Inline edit</strong>
                </div>
            </div>
        </section>

        @if ($categoriesError)
            <div class="alert alert-danger" role="alert">{{ $categoriesError }}</div>
        @endif

        <div class="admin-table-wrap" id="category-table">
            <table class="admin-table full-width">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Name</th>
                        <th>Slug</th>
                        <th>Description</th>
                        <th class="col-actions">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse ($categories as $category)
                        <tr>
                            <td>{{ $category['id'] }}</td>
                            <td>{{ $category['name'] }}</td>
                            <td><code class="dashboard-code-chip">{{ $category['slug'] }}</code></td>
                            <td>{{ Str::limit($category['descriptions'] ?? '', 50) }}</td>
                            <td class="table-actions-cell">
                                <details class="admin-inline-details">
                                    <summary class="btn-small">Chỉnh sửa</summary>
                                    <form method="POST" action="{{ route('admin.categories.update', $category['id']) }}" class="admin-form admin-edit-form admin-edit-grid">
                                        @csrf
                                        @method('PUT')
                                        <div class="form-group">
                                            <label>Tên</label>
                                            <input id="category_name_{{ $category['id'] }}" name="name" type="text"
                                                class="form-control" value="{{ $category['name'] }}"
                                                data-slug-target="#category_slug_{{ $category['id'] }}">
                                        </div>
                                        <div class="form-group">
                                            <label>Slug</label>
                                            <input id="category_slug_{{ $category['id'] }}" name="slug" type="text"
                                                class="form-control" value="{{ $category['slug'] }}">
                                        </div>
                                        <div class="form-group form-group-full">
                                            <label>Mô tả</label>
                                            <textarea name="descriptions" class="form-control" rows="2">{{ $category['descriptions'] ?? '' }}</textarea>
                                        </div>
                                        <div class="admin-edit-actions">
                                            <button type="submit" class="btn-small">Lưu</button>
                                        </div>
                                    </form>
                                </details>
                                <form method="POST" action="{{ route('admin.categories.delete', $category['id']) }}" class="d-inline">
                                    @csrf
                                    @method('DELETE')
                                    <button type="submit" class="btn-small btn-danger"
                                        onclick="return confirm('Xoa danh muc nay?')">Xoá</button>
                                </form>
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="5">Không có danh mục để hiển thị.</td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        <div class="admin-form-wrapper" id="category-create-section">
            <button type="button" class="btn-secondary admin-form-toggle" data-toggle-target="#category-create-form" data-label-open="Mở form tạo danh mục" data-label-close="Đóng form tạo danh mục">Mở form tạo danh mục</button>
            <div id="category-create-form" class="admin-form-panel" hidden>
                <form method="POST" action="{{ route('admin.categories.store') }}" class="admin-form admin-form-grid">
                    @csrf
                    <div class="form-group">
                        <label for="category_name">Tên danh mục</label>
                        <input id="category_name" name="name" type="text" class="form-control" required
                            data-slug-target="#category_slug">
                    </div>
                    <div class="form-group">
                        <label for="category_slug">Slug</label>
                        <input id="category_slug" name="slug" type="text" class="form-control" required>
                    </div>
                    <div class="form-group form-group-full">
                        <label for="category_descriptions">Mô tả</label>
                        <textarea id="category_descriptions" name="descriptions" class="form-control" rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn-primary">Tạo danh mục</button>
                </form>
            </div>
        </div>
    </div>
@endsection
