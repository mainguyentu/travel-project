@extends('layouts.admin')

@section('title', 'Quản lý categories')

@section('content')
<div class="page-head"><div><h1>Categories</h1><p class="muted">Thể loại điểm đến</p></div></div>
<form method="POST" action="{{ route('admin.categories.store') }}" class="toolbar">
    @csrf
    <input type="text" name="name" placeholder="Tên" required maxlength="120">
    <input type="text" name="slug" placeholder="slug" required maxlength="160">
    <input type="text" name="descriptions" placeholder="Mô tả">
    <button type="submit">Tạo</button>
</form>
<table class="admin-table">
    <thead><tr><th>ID</th><th>Tên</th><th>Slug</th><th>Hành động</th></tr></thead>
    <tbody>
    @foreach ($categories as $c)
        <tr>
            <td>{{ $c['id'] }}</td>
            <td>{{ $c['name'] }}</td>
            <td>{{ $c['slug'] }}</td>
            <td>
                <form method="POST" action="{{ route('admin.categories.update', ['id' => $c['id']]) }}" class="inline-form">
                    @csrf @method('PUT')
                    <input type="text" name="name" value="{{ $c['name'] }}">
                    <button type="submit" class="btn-small">Sửa</button>
                </form>
                <form method="POST" action="{{ route('admin.categories.delete', ['id' => $c['id']]) }}" class="inline-form" onsubmit="return confirm('Xóa category này?')">
                    @csrf @method('DELETE')
                    <button type="submit" class="btn-danger">Xóa</button>
                </form>
            </td>
        </tr>
    @endforeach
    </tbody>
</table>
@endsection
