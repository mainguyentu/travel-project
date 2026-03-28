@extends('layouts.admin')

@section('page-title', 'Categories Management')

@section('content')
    <div class="admin-section">
        <div class="section-header">
            <h2>Categories Management</h2>
            <a href="#" class="btn-primary">Add Category</a>
        </div>

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
                            <div class="actions">
                                <a href="#" class="btn-small">Edit</a>
                                <button class="btn-small btn-danger" data-category-id="{{ $category['id'] }}">Delete</button>
                            </div>
                        </td>
                    </tr>
                @empty
                    <tr><td colspan="5">No categories found</td></tr>
                @endforelse
            </tbody>
        </table>
    </div>
@endsection

