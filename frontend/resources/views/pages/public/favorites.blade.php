@extends('layouts.app')

@section('title', 'My Favorites - Alats Travel')

@section('content')
    <section class="public-shell">
        <div class="site-container">
            <header class="public-page-header">
                <h1>Điểm đến yêu thích</h1>
                <p>Danh sách địa điểm bạn đã lưu.</p>
            </header>

            @if (session('success'))
                <div class="alert alert-success" role="status">{{ session('success') }}</div>
            @endif

            @if ($favoritesError)
                <div class="alert alert-error" role="alert">
                    <strong>Không thể tải danh sách yêu thích.</strong>
                    <p>{{ $favoritesError }}</p>
                </div>
            @endif

            @error('favorites')
                <div class="alert alert-error" role="alert">{{ $message }}</div>
            @enderror

            @error('rating')
                <div class="alert alert-error" role="alert">{{ $message }}</div>
            @enderror

            @if (count($favorites) > 0)
                <div class="destination-grid">
                    @foreach ($favorites as $destination)
                        @include('components.destination-card', ['destination' => $destination, 'isFavorite' => true])
                    @endforeach
                </div>
            @else
                <div class="empty-state">
                    <p>Bạn chưa có địa điểm yêu thích nào.</p>
                    <a href="{{ route('destinations.index') }}" class="btn-primary">Bắt đầu khám phá</a>
                </div>
            @endif

            @component('components.destination-detail-modal', ['destinations' => $favorites])
            @endcomponent
        </div>
    </section>
@endsection
