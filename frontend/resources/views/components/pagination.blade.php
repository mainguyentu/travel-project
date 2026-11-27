@props(['meta' => [], 'query' => []])
@php($page = (int) ($meta['page'] ?? 1))
<div class="pagination">
    @if ($page > 1)
        <a href="{{ route('destinations.index', array_merge($query, ['page' => $page - 1])) }}">‹ Trước</a>
    @endif
    <span>Trang {{ $page }}</span>
    <a href="{{ route('destinations.index', array_merge($query, ['page' => $page + 1])) }}">Sau ›</a>
</div>
