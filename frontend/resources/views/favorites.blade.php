@extends('layouts.public')

@section('title', 'Yêu thích của tôi')

@section('content')
<div class="container">
    <div class="section-head" style="margin-top:1.5rem">
        <h2>Yêu thích <span class="grad-text">của tôi</span></h2>
        <p>Những địa điểm bạn đã lưu lại</p>
    </div>
    <div class="grid">
        @forelse ($destinations as $d)
            <div>
                <x-destination-card :destination="$d" />
                <form method="POST" action="{{ route('favorites.remove', ['id' => $d['id']]) }}" class="inline-form">
                    @csrf
                    @method('DELETE')
                    <button type="submit" class="link-btn">Bỏ yêu thích</button>
                </form>
                <x-rating-form :destinationId="$d['id']" />
            </div>
        @empty
            <p>Chưa có địa điểm yêu thích nào. <a href="{{ route('destinations.index') }}">Khám phá ngay</a>.</p>
        @endforelse
    </div>
    <x-destination-detail-modal />
</div>
@endsection

@push('scripts')
<script>
// Cùng origin qua gateway (xem destinations/index).
window.API_BASE = @json(url('/api/v1'));
</script>
@endpush
