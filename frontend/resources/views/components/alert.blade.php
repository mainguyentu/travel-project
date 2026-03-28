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

