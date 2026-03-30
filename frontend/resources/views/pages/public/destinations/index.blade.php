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
                    {{-- <form action="{{ route('destinations.index') }}" method="GET">
                        <div class="filter-group">
                            <label for="category">Danh mục</label>
                            <select class="public-select" name="category_slug" id="category">
                                <option value="">Tất cả danh mục</option>
                                @foreach ($categories as $category)
                                    <option value="{{ $category['slug'] }}"
                                        {{ (request('category_slug') ?? request('category')) === $category['slug'] ? 'selected' : '' }}>
                                        {{ $category['name'] }}
                                    </option>
                                @endforeach
                            </select>
                        </div>

                        <div class="filter-group">
                            <label for="price_level">Mức giá</label>
                            <select class="public-select" name="price_level" id="price_level">
                                <option value="">Tất cả</option>
                                <option value="1" {{ request('price_level') === '1' ? 'selected' : '' }}>$ - Tiết kiệm
                                </option>
                                <option value="2" {{ request('price_level') === '2' ? 'selected' : '' }}>$$ - Vừa phải
                                </option>
                                <option value="3" {{ request('price_level') === '3' ? 'selected' : '' }}>$$$ - Cao cấp
                                </option>
                            </select>
                        </div>

                        <div class="filter-group">
                            <label for="rating">Đánh giá tối thiểu</label>
                            <select class="public-select" name="rating_min" id="rating">
                                <option value="">Tất cả</option>
                                <option value="4.5"
                                    {{ (request('rating_min') ?? request('rating')) === '4.5' ? 'selected' : '' }}>4.5+ ⭐
                                </option>
                                <option value="4"
                                    {{ (request('rating_min') ?? request('rating')) === '4' ? 'selected' : '' }}>4+ ⭐
                                </option>
                                <option value="3.5"
                                    {{ (request('rating_min') ?? request('rating')) === '3.5' ? 'selected' : '' }}>3.5+ ⭐
                                </option>
                            </select>
                        </div>

                        <div class="filter-actions">
                            <button type="submit" class="btn-primary btn-block">Áp dụng bộ lọc</button>
                            <a href="{{ route('destinations.index') }}" class="btn-secondary btn-block">Đặt lại</a>
                        </div>
                    </form> --}}
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

