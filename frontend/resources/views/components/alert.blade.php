@if ($type === 'success' || $type === 'info')
    <div class="alert alert-{{ $type }}">
        <strong>{{ $title ?? 'Thông Báo' }}</strong>
        @if (isset($message))
            <p>{{ $message }}</p>
        @elseif (isset($messages))
            <ul>
                @foreach ($messages as $msg)
                    <li>{{ $msg }}</li>
                @endforeach
            </ul>
        @endif
    </div>
@elseif ($type === 'danger' || $type === 'error')
    <div class="alert alert-danger">
        <strong>{{ $title ?? 'Lỗi' }}</strong>
        @if (isset($messages) && is_array($messages))
            <ul>
                @foreach ($messages as $msg)
                    <li>{{ $msg }}</li>
                @endforeach
            </ul>
        @elseif (isset($message))
            <p>{{ $message }}</p>
        @endif
    </div>
@endif

<style>
    .alert {
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }

    .alert-success {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }

    .alert-info {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }

    .alert-danger {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }

    .alert strong {
        display: block;
        margin-bottom: 0.5rem;
    }

    .alert ul {
        margin: 0;
        padding-left: 1.5rem;
    }

    .alert li {
        margin-bottom: 0.25rem;
    }
</style>
