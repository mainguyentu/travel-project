<div class="rating-form">
    <h4>Đánh Giá Địa Điểm Này</h4>

    <form id="ratingForm" method="POST" action="{{ route('ratings.store', $destinationId) }}">
        @csrf
        @method('PUT')

        <div class="form-group">
            <label for="rating">Đánh Giá (Sao)</label>
            <div class="star-rating">
                @for ($i = 1; $i <= 5; $i++)
                          <input type="radio" name="rating_score" id="star{{ $i }}" value="{{ $i }}" 
                           @if($currentRating == $i) checked @endif>
                    <label for="star{{ $i }}" class="star">★</label>
                @endfor
            </div>
        </div>

        <div class="form-group">
            <label for="comment">Nhận Xét (Tùy Chọn)</label>
            <textarea name="comment" id="comment" rows="4" class="form-control" 
                      placeholder="Chia sẻ trải nghiệm của bạn...">{{ $currentComment ?? '' }}</textarea>
        </div>

        <button type="submit" class="btn btn-primary">Gửi Đánh Giá</button>
    </form>
</div>

