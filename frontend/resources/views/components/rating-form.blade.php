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

<style>
    .rating-form {
        background: #f9f9f9;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 2rem 0;
    }

    .rating-form h4 {
        margin-top: 0;
        color: #333;
    }

    .form-group {
        margin-bottom: 1.5rem;
    }

    .form-group label {
        display: block;
        margin-bottom: 0.5rem;
        color: #333;
        font-weight: 500;
    }

    .star-rating {
        display: flex;
        gap: 0.5rem;
        font-size: 2rem;
    }

    .star-rating input {
        display: none;
    }

    .star {
        cursor: pointer;
        color: #ddd;
        transition: color 0.3s;
    }

    .star-rating input:checked ~ label,
    .star:hover,
    .star-rating input:checked ~ label ~ .star:hover {
        color: #ffc107;
    }

    .form-control {
        width: 100%;
        padding: 0.75rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-family: inherit;
        resize: vertical;
    }

    .form-control:focus {
        outline: none;
        border-color: #0066cc;
        box-shadow: 0 0 0 3px rgba(0,102,204,0.1);
    }
</style>
