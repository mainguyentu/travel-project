@props(['destinationId'])
<form method="POST" action="{{ route('ratings.store', ['id' => $destinationId]) }}" class="rating-form" aria-label="Gửi đánh giá">
    @csrf
    @method('PUT')
    <label for="rating-score-{{ $destinationId }}">Chấm điểm (1–5)</label>
    <input id="rating-score-{{ $destinationId }}" type="number" name="rating_score" min="1" max="5" required>
    <label class="sr-only" for="rating-comment-{{ $destinationId }}">Nhận xét (tùy chọn)</label>
    <input id="rating-comment-{{ $destinationId }}" type="text" name="comment" placeholder="Nhận xét (tùy chọn)" maxlength="1000">
    <button type="submit">Gửi đánh giá</button>
</form>
