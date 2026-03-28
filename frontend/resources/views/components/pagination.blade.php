<div class="pagination-wrapper">
    @if ($items->hasPages())
        <nav class="pagination">
            {{-- Previous Page Link --}}
            @if ($items->onFirstPage())
                <span class="page-link disabled">← Trước</span>
            @else
                <a href="{{ $items->previousPageUrl() }}" class="page-link">← Trước</a>
            @endif

            {{-- Pagination Elements --}}
            @foreach ($items->getUrlRange(1, $items->lastPage()) as $page => $url)
                @if ($page == $items->currentPage())
                    <span class="page-link active">{{ $page }}</span>
                @else
                    <a href="{{ $url }}" class="page-link">{{ $page }}</a>
                @endif
            @endforeach

            {{-- Next Page Link --}}
            @if ($items->hasMorePages())
                <a href="{{ $items->nextPageUrl() }}" class="page-link">Tiếp →</a>
            @else
                <span class="page-link disabled">Tiếp →</span>
            @endif
        </nav>
    @endif
</div>

