@extends('layouts.admin')

@section('title', 'Thống kê')

@section('content')
<div class="page-head"><div><h1>Thống kê tổng hợp</h1><p class="muted">Nguồn tìm kiếm: {{ $searchEngine ?? 'DB' }}</p></div></div>
<div class="panels">
    <section class="panel">
        <h2>Top yêu thích</h2>
        <table class="admin-table">
            <thead><tr><th>Tên</th><th>Lượt xem</th></tr></thead>
            <tbody>
            @foreach ($topFavorites as $d)
                <tr><td>{{ $d['name'] }}</td><td>{{ $d['view_count'] ?? 0 }}</td></tr>
            @endforeach
            </tbody>
        </table>
    </section>
    <section class="panel">
        <h2>Top rating</h2>
        <table class="admin-table">
            <thead><tr><th>Tên</th><th>Rating</th></tr></thead>
            <tbody>
            @foreach ($topRatings as $d)
                <tr><td>{{ $d['name'] }}</td><td>★ {{ $d['rating_avg'] ?? 0 }}</td></tr>
            @endforeach
            </tbody>
        </table>
    </section>
    <section class="panel">
        <h2>Top lượt xem</h2>
        <table class="admin-table">
            <thead><tr><th>Tên</th><th>Lượt xem</th></tr></thead>
            <tbody>
            @foreach ($topViews as $d)
                <tr><td>{{ $d['name'] }}</td><td>{{ $d['view_count'] ?? 0 }}</td></tr>
            @endforeach
            </tbody>
        </table>
    </section>
</div>
@endsection
