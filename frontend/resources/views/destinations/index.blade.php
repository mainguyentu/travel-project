@extends('layouts.public')

@section('title', 'Địa điểm — Alats Travel')

@section('content')
<div class="container">
    <div class="section-head" style="margin-top:1.5rem">
        <h2>Địa điểm <span class="grad-text">Đà Nẵng</span></h2>
        <p>Tìm kiếm và lọc theo thể loại, mức giá, đánh giá</p>
    </div>
    <x-filter-panel :filters="$filters" :query="$query" />
    <p class="muted">Tổng: {{ $meta['total'] ?? 0 }}
    @if (! empty($meta['search_engine']))
        · Tìm kiếm: {{ $meta['search_engine'] === 'elasticsearch' ? 'Elasticsearch' : 'DB' }}
    @endif
    </p>
    <div class="grid">
        @forelse ($destinations as $d)
            <x-destination-card :destination="$d" :favorited="in_array($d['id'] ?? 0, $favoriteIds ?? [])" />
        @empty
            <p class="muted">Không tìm thấy địa điểm phù hợp.</p>
        @endforelse
    </div>
    <x-pagination :meta="$meta" :query="$query" />
    <x-destination-detail-modal />
</div>
@endsection

@push('scripts')
<script>
// Cùng origin qua gateway (nginx proxy /api/v1/ → backend). Không dùng
// config api.base_url ở đây vì đó là hostname nội bộ Docker (backend:8000).
window.API_BASE = @json(url('/api/v1'));
</script>
@endpush
