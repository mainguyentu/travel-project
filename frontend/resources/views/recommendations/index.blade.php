@extends('layouts.public')

@section('title', 'Gợi ý dành cho bạn')

@section('content')
<div class="container">
    <div class="section-head" style="margin-top:1.5rem">
        <h2>Đề xuất <span class="grad-text">dành cho bạn</span></h2>
        <p>Tính từ điểm insight tổng hợp (Google Maps &amp; trang du lịch) + sở thích và thói quen của bạn —
            bạn chỉ cần tham khảo, không cần đánh giá.</p>
    </div>

    @if (! empty($profile['top_categories']))
        <p class="muted">Gu của bạn:
            @foreach ($profile['top_categories'] as $slug => $w)
                <span class="chip">{{ $slug }} · {{ $w }}</span>
            @endforeach
            @if (! empty($profile['preferred_price']))
                <span class="chip">giá {{ $profile['preferred_price'] }}</span>
            @endif
        </p>
    @else
        <p class="muted">Bạn mới tham khảo nên gợi ý theo độ hot toàn site — hãy ♥ vài nơi bạn thích để gợi ý chuẩn hơn.</p>
    @endif

    <section class="section">
        <div class="section-head"><h2>Phù hợp <span class="grad-text">với bạn</span></h2></div>
        <div class="grid">
            @forelse ($matched as $s)
                <div>
                    <x-destination-card :destination="$s['destination']" :favorited="in_array($s['destination']['id'] ?? 0, $favoriteIds ?? [])" />
                    <ul class="reco-reasons">
                        <li>Khớp {{ $s['match'] }}%</li>
                        @foreach ($s['reasons'] ?? [] as $r)
                            <li>{{ $r }}</li>
                        @endforeach
                    </ul>
                </div>
            @empty
                <p>Chưa có gợi ý phù hợp. <a href="{{ route('destinations.index') }}">Khám phá thêm</a>.</p>
            @endforelse
        </div>
    </section>

    <section class="section section-alt">
        <div class="section-head"><h2>Có thể <span class="grad-text">bạn sẽ thích</span></h2></div>
        <div class="grid">
            @forelse ($explore as $s)
                <div>
                    <x-destination-card :destination="$s['destination']" :favorited="in_array($s['destination']['id'] ?? 0, $favoriteIds ?? [])" />
                    <ul class="reco-reasons">
                        <li>Khớp {{ $s['match'] }}%</li>
                        @foreach ($s['reasons'] ?? [] as $r)
                            <li>{{ $r }}</li>
                        @endforeach
                    </ul>
                </div>
            @empty
                <p>Chưa có gợi ý khám phá.</p>
            @endforelse
        </div>
    </section>

    <section class="section">
        <div class="section-head">
            <h2>Lịch trình <span class="grad-text">gợi ý ({{ $totalMatch }}% hợp)</span></h2>
            <p>Sắp xếp để không trùng gu liên tiếp</p>
        </div>
        <form method="GET" action="{{ route('recommendations.index') }}" class="toolbar">
            <label class="sr-only" for="days">Số điểm</label>
            <select id="days" name="days">
                @foreach ([3, 5, 7] as $n)
                    <option value="{{ $n }}" @selected($planDays == $n)>{{ $n }} điểm</option>
                @endforeach
            </select>
            <button type="submit">Tạo lịch trình</button>
        </form>
        @forelse ($itinerary as $step)
            <div class="panel itinerary-step" style="margin-bottom:0.8rem">
                <span class="itinerary-order">{{ $step['order'] }}</span>
                <div>
                    <strong>{{ $step['destination']['name'] ?? '' }}</strong>
                    <span class="itinerary-slot"> · buổi {{ $step['slot'] ?? 'tự do' }} · khớp {{ $step['match'] }}%</span>
                    <ul class="reco-reasons">
                        @foreach ($step['reasons'] ?? [] as $r)
                            <li>{{ $r }}</li>
                        @endforeach
                    </ul>
                    <div style="margin-top:0.4rem">
                        <button type="button" class="link-btn" data-detail="{{ $step['destination']['id'] ?? '' }}">Xem chi tiết →</button>
                    </div>
                </div>
            </div>
        @empty
            <p>Chưa có lịch trình.</p>
        @endforelse
        <x-destination-detail-modal />
    </section>
</div>
@endsection

@push('scripts')
<script>
window.API_BASE = @json(url('/api/v1'));
</script>
@endpush
