@php
    $destinations = is_array($destinations ?? null) ? $destinations : [];
@endphp

<div class="destination-modal" data-destination-modal
    data-rating-endpoint="{{ url('/ratings') }}"
    data-favorites-add-endpoint="{{ url('/favorites') }}"
    data-can-rate="{{ session()->has('access_token') ? 'true' : 'false' }}"
    data-can-favorite="{{ session()->has('access_token') ? 'true' : 'false' }}"
    data-login-url="{{ route('login') }}" hidden>
    <div class="destination-modal-backdrop" data-close-destination-modal></div>
    <div class="destination-modal-dialog panel" role="dialog" aria-modal="true"
        aria-labelledby="destination-modal-title" tabindex="-1">
        <div class="destination-modal-header">
            <h2 id="destination-modal-title">Đang tải chi tiết...</h2>
            <button type="button" class="destination-modal-close" data-close-destination-modal
                aria-label="Đóng popup">×</button>
        </div>

        <div class="destination-modal-content" data-destination-modal-content>
            <p class="muted">Vui lòng chờ trong giây lát...</p>
        </div>
    </div>
    <script type="application/json" data-destination-dataset>@json($destinations)</script>
</div>

<div class="destination-modal rating-modal" data-rating-modal hidden>
    <div class="destination-modal-backdrop" data-close-rating-modal></div>
    <div class="destination-modal-dialog panel" role="dialog" aria-modal="true"
        aria-labelledby="rating-modal-title" tabindex="-1">
        <div class="destination-modal-header">
            <h2 id="rating-modal-title">Đánh giá địa điểm</h2>
            <button type="button" class="destination-modal-close" data-close-rating-modal
                aria-label="Đóng popup">×</button>
        </div>

        <div class="destination-modal-content">
            <div class="rating-form">
                <form data-rating-form method="POST" action="#">
                    @csrf
                    @method('PUT')

                    <div class="form-group">
                        <label for="rating-score">Đánh giá (sao)</label>
                        <div class="star-rating">
                            @for ($i = 1; $i <= 5; $i++)
                                <input type="radio" name="rating_score" id="rating-star-{{ $i }}" value="{{ $i }}">
                                <label for="rating-star-{{ $i }}" class="star">★</label>
                            @endfor
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="rating-comment">Nhận xét (tùy chọn)</label>
                        <textarea name="comment" id="rating-comment" rows="4" class="form-control"
                            placeholder="Chia sẻ trải nghiệm của bạn..."></textarea>
                    </div>

                    <button type="submit" class="btn btn-primary">Gửi đánh giá</button>
                </form>
            </div>
        </div>
    </div>
</div>
