@props(['filters' => [], 'query' => []])
<form method="GET" action="{{ route('destinations.index') }}" class="filters" aria-label="Lọc điểm đến">
    <label class="sr-only" for="f-cat">Thể loại</label>
    <select id="f-cat" name="category_slug">
        <option value="">Tất cả thể loại</option>
        @foreach ($filters as $c)
            <option value="{{ $c['slug'] }}" @selected(($query['category_slug'] ?? '') === $c['slug'])>{{ $c['name'] }}</option>
        @endforeach
    </select>
    <label class="sr-only" for="f-price">Mức giá</label>
    <select id="f-price" name="price_level">
        <option value="">Mọi mức giá</option>
        @foreach (['free', 'low', 'medium', 'high'] as $p)
            <option value="{{ $p }}" @selected(($query['price_level'] ?? '') === $p)>{{ $p }}</option>
        @endforeach
    </select>
    <label class="sr-only" for="f-kw">Từ khóa</label>
    <input id="f-kw" type="text" name="keyword" placeholder="Từ khóa…" value="{{ $query['keyword'] ?? '' }}">
    <label class="sr-only" for="f-sort">Sắp xếp</label>
    <select id="f-sort" name="sort">
        <option value="">Mới nhất</option>
        <option value="rating" @selected(($query['sort'] ?? '') === 'rating')>Rating cao</option>
        <option value="views" @selected(($query['sort'] ?? '') === 'views')>Xem nhiều</option>
        <option value="name" @selected(($query['sort'] ?? '') === 'name')>Tên A–Z</option>
    </select>
    <button type="submit">Lọc</button>
</form>
