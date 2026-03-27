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

<style>
    .pagination-wrapper {
        margin-top: 2rem;
        display: flex;
        justify-content: center;
    }

    .pagination {
        display: flex;
        gap: 0.25rem;
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .page-link {
        padding: 0.5rem 0.75rem;
        border: 1px solid #ddd;
        background: white;
        color: #0066cc;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.3s;
        border-radius: 4px;
        display: inline-block;
    }

    .page-link:hover:not(.disabled) {
        background: #0066cc;
        color: white;
    }

    .page-link.active {
        background: #0066cc;
        color: white;
        border-color: #0066cc;
    }

    .page-link.disabled {
        color: #999;
        cursor: not-allowed;
        background: #f5f5f5;
    }
</style>
