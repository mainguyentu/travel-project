@extends('layouts.admin')

@section('title', 'Quản lý destinations')

@section('content')
<div class="page-head"><div><h1>Destinations</h1><p class="muted">Tổng {{ $meta['total'] ?? 0 }}</p></div></div>
<form method="GET" action="{{ route('admin.destinations.index') }}" class="toolbar">
    <input type="text" name="keyword" placeholder="Từ khóa…" value="{{ request('keyword') }}">
    <select name="status">
        <option value="">Mọi trạng thái</option>
        <option value="active" @selected(request('status') === 'active')>active</option>
        <option value="inactive" @selected(request('status') === 'inactive')>inactive</option>
    </select>
    <button type="submit">Lọc</button>
</form>
<form method="POST" action="{{ route('admin.destinations.store') }}" class="toolbar">
    @csrf
    <input type="text" name="name" placeholder="Tên" required maxlength="180">
    <input type="text" name="slug" placeholder="slug" required maxlength="220">
    <select name="price_level">
        <option value="free">free</option>
        <option value="low">low</option>
        <option value="medium" selected>medium</option>
        <option value="high">high</option>
    </select>
    <input type="text" name="category_slugs" placeholder="category slugs, cách nhau bằng dấu phẩy">
    <button type="submit">Tạo</button>
</form>
<details class="admin-details">
    <summary>Bulk import (JSON mảng items)</summary>
    <form method="POST" action="{{ route('admin.destinations.bulk') }}">
        @csrf
        <textarea name="payload" rows="4" placeholder='[{"name":"A","slug":"a"}]' required></textarea>
        <button type="submit" class="btn-small" style="margin-top:0.5rem">Bulk import</button>
    </form>
</details>
<table class="admin-table">
    <thead><tr><th>ID</th><th>Ảnh</th><th>Tên</th><th>Slug</th><th>Giá</th><th>Rating</th><th>Views</th><th>Status</th><th>Hành động</th></tr></thead>
    <tbody>
    @foreach ($destinations as $d)
        <tr>
            <td>{{ $d['id'] }}</td>
            <td>
                @if (! empty($d['img_url']))
                    <img class="thumb" src="{{ $d['img_url'] }}" alt="" loading="lazy">
                @else
                    <span class="thumb-ph">{{ mb_substr($d['name'] ?? '?', 0, 1) }}</span>
                @endif
            </td>
            <td>{{ $d['name'] }}</td>
            <td class="muted">{{ $d['slug'] }}</td>
            <td>{{ $d['price_level'] ?? '' }}</td>
            <td>★ {{ $d['rating_avg'] ?? 0 }}</td>
            <td>{{ $d['view_count'] ?? 0 }}</td>
            <td><span class="badge {{ ($d['status'] ?? '') === 'active' ? 'badge-ok' : 'badge-locked' }}">{{ $d['status'] ?? '' }}</span></td>
            <td>
                <form method="POST" action="{{ route('admin.destinations.delete', ['id' => $d['id']]) }}" class="inline-form" onsubmit="return confirm('Xóa destination này?')">
                    @csrf @method('DELETE')
                    <button type="submit" class="btn-danger">Xóa</button>
                </form>
            </td>
        </tr>
    @endforeach
    </tbody>
</table>
@endsection
