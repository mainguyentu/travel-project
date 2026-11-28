@props(['destination'])
@php
    $extCount = (int) ($destination['external_rating_count'] ?? 0);
    $ins = $destination['insight'] ?? null;
    if ($extCount > 0) {
        $avg = (float) ($destination['external_rating_avg'] ?? 0);
        $count = $extCount;
        $src = $destination['external_source'] ?? 'nguồn chính thống';
        $srcLabel = $src === 'google_maps' ? 'Google Maps' : str_replace('_', ' ', $src);
    } else {
        $avg = (float) ($ins['rating_avg'] ?? $destination['rating_avg'] ?? 0);
        $count = (int) ($ins['rating_count'] ?? $destination['metrics']['rating_count'] ?? 0);
        $srcLabel = 'đánh giá trên trang';
    }
@endphp
<div class="rating-summary" aria-label="Điểm tổng hợp">
    <span class="rs-score">★ {{ number_format($avg, 1) }}</span>
    <span>({{ number_format($count) }} đánh giá · {{ $srcLabel }})</span>
    @if (! $extCount && ($ins['status'] ?? '') !== 'ok')
        <div class="rs-src">Ít dữ liệu — tham khảo thêm trước khi đi.</div>
    @endif
</div>
