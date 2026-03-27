@extends('layouts.app')

@section('title', 'My Favorites - Alats Travel')

@section('content')
    <section class="public-shell">
        <div class="site-container">
            <header class="public-page-header">
                <h1>Điểm đến yêu thích</h1>
                <p>Đanh sách địa điểm bạn đã lưu.</p>
            </header>

            @if (count($favorites) > 0)
                <div class="destination-grid">
                    @foreach ($favorites as $destination)
                        @include('components.destination-card', ['destination' => $destination])
                    @endforeach
                </div>
            @else
                <div class="empty-state">
                    <p>Bạn chưa có địa điểm yêu thích nào.</p>
                    <a href="{{ route('destinations.index') }}" class="btn-primary">Bắt đầu khám phá</a>
                </div>
            @endif
        </div>
    </section>
@endsection
