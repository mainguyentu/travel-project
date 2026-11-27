@extends('layouts.admin')

@section('title', 'Admin dashboard')

@section('content')
<div class="page-head">
    <div>
        <h1>Dashboard</h1>
        <p class="muted">Tổng quan vận hành · nguồn tìm kiếm: {{ $searchEngine ?? 'DB' }}</p>
    </div>
</div>

<div class="kpis">
    <div class="kpi"><div class="kpi-num">{{ count($topViews ?? []) }}</div><div class="kpi-label">Top lượt xem</div></div>
    <div class="kpi"><div class="kpi-num">{{ count($topFavorites ?? []) }}</div><div class="kpi-label">Top yêu thích</div></div>
    <div class="kpi"><div class="kpi-num">{{ count($topRatings ?? []) }}</div><div class="kpi-label">Top rating</div></div>
</div>

<form method="GET" action="{{ route('admin.dashboard') }}" class="filters">
    <label>Từ <input type="date" name="from" value="{{ $from ?? '' }}"></label>
    <label>Đến <input type="date" name="to" value="{{ $to ?? '' }}"></label>
    <button type="submit">Lọc</button>
</form>

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
