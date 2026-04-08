@extends('layouts.app')

@section('title', 'Destinations - Alats Travel')

@section('content')
    <section class="public-shell">
        <div class="site-container">
            <header class="public-page-header">
                <h1>Khám phá điểm đến</h1>
                <p>Lọc kết quả theo danh mục, mức chi phí và đánh giá để tìm địa điểm phù hợp nhất.</p>
            </header>

            @if ($listError)
                <div class="alert alert-error" role="alert">
                    <strong>Không thể tải danh sách điểm đến.</strong>
                    <p>{{ $listError }}</p>
                </div>
            @endif

            <div class="destinations-layout">
                <aside class="filter-panel panel">
                    <h2 class="filter-panel-title">Bộ lọc</h2>
                    @include('components.filter-panel')
                </aside>

                <div>
                    <p class="muted list-result-count">
                        Tìm thấy {{ (int) ($pagination['total'] ?? count($destinations)) }} kết quả.
                    </p>

                    <div class="destination-grid">
                        @forelse ($destinations as $destination)
                            @include('components.destination-card', ['destination' => $destination])
                        @empty
                            <div class="empty-state destination-empty-state">
                                <p>Chưa tìm thấy địa điểm phù hợp với bộ lọc hiện tại.</p>
                            </div>
                        @endforelse
                    </div>

                    @php
                        $currentPage = (int) ($pagination['current_page'] ?? 1);
                        $lastPage = (int) ($pagination['last_page'] ?? 1);
                        $baseQuery = request()->except('page');
                    @endphp

                    @if ($lastPage > 1)
                        <nav class="pagination" aria-label="Pagination">
                            @if ($currentPage > 1)
                                <a
                                    href="{{ route('destinations.index', array_merge($baseQuery, ['page' => $currentPage - 1])) }}">←
                                    Trước</a>
                            @else
                                <span>← Trước</span>
                            @endif

                            @for ($page = 1; $page <= $lastPage; $page++)
                                @if ($page === $currentPage)
                                    <span class="active">{{ $page }}</span>
                                @else
                                    <a
                                        href="{{ route('destinations.index', array_merge($baseQuery, ['page' => $page])) }}">{{ $page }}</a>
                                @endif
                            @endfor

                            @if ($currentPage < $lastPage)
                                <a
                                    href="{{ route('destinations.index', array_merge($baseQuery, ['page' => $currentPage + 1])) }}">Tiếp
                                    →</a>
                            @else
                                <span>Tiếp →</span>
                            @endif
                        </nav>
                    @endif
                </div>
            </div>

            @component('components.destination-detail-modal')
            @endcomponent
        </div>
    </section>
@endsection
