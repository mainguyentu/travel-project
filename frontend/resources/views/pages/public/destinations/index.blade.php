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
                @include('components.filter-panel')

                <div class="destinations-results">
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
                        $currentPage = max((int) ($pagination['current_page'] ?? 1), 1);
                        $lastPage = max((int) ($pagination['last_page'] ?? 1), 1);
                        $pageNodes = collect([1, 2, $currentPage - 1, $currentPage, $currentPage + 1, $lastPage - 1, $lastPage])
                                    ->filter(fn($page) => $page >= 1 && $page <= $lastPage)
                                    ->unique()
                                    ->sort()
                                    ->values();
                        // $baseQuery = request()->except('page');
                    @endphp

                    @if ($lastPage > 1)
                        <div class="pagination-wrapper" aria-label="Destination pagination">
                            <nav class="pagination">
                                @if ($currentPage > 1)
                                    <a href="{{ route('destinations.index', array_merge(request()->except('page'), ['page' => $currentPage - 1])) }}"
                                        class="page-link">Prev</a>
                                @else
                                    <span class="page-link disabled">Prev</span>
                                @endif

                                @php
                                    $previousPrinted = null;
                                @endphp
                                @foreach ($pageNodes as $pageNode)
                                    @if ($previousPrinted !== null && $pageNode - $previousPrinted > 1)
                                        <span class="page-link dots">...</span>
                                    @endif

                                    @if ($pageNode === $currentPage)
                                        <span class="page-link active">{{ $pageNode }}</span>
                                    @else
                                        <a href="{{ route('destinations.index', array_merge(request()->except('page'), ['page' => $pageNode])) }}"
                                            class="page-link">{{ $pageNode }}</a>
                                    @endif

                                    @php
                                        $previousPrinted = $pageNode;
                                    @endphp
                                @endforeach

                                @if ($currentPage < $lastPage)
                                    <a href="{{ route('destinations.index', array_merge(request()->except('page'), ['page' => $currentPage + 1])) }}"
                                        class="page-link">Next</a>
                                @else
                                    <span class="page-link disabled">Next</span>
                                @endif

                            </nav>
                        </div>
                    @endif
                </div>
            </div>

            @component('components.destination-detail-modal', ['destinations' => $destinations])
            @endcomponent
        </div>
    </section>
@endsection
