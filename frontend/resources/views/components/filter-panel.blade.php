<div class="filter-panel filter-panel--horizontal">
    @php
        $selectedPriceLevel = (string) request('price_level', '');
    @endphp

    <form method="GET" action="{{ route('destinations.index') }}" id="filterForm" class="filter-panel-form">
        <div class="filter-panel-row filter-panel-row--top">
            <div class="filter-group filter-group--search">
                <label for="search">Từ khóa</label>
                <input type="text" name="keyword" id="search" class="form-control" placeholder="Tên địa điểm..."
                    value="{{ request('keyword', request('search')) }}">
            </div>

            <div class="filter-group">
                <label for="priceLevel">Mức giá</label>
                <select name="price_level" id="priceLevel" class="form-control">
                    <option value="">Tất cả</option>
                    <option value="low" @selected($selectedPriceLevel === 'low')>$ - Tiết kiệm</option>
                    <option value="medium" @selected($selectedPriceLevel === 'medium')>$$ - Vừa phải</option>
                    <option value="high" @selected($selectedPriceLevel === 'high')>$$$ - Cao cấp</option>
                </select>
            </div>

            <div class="filter-buttons">
                <button type="submit" class="btn btn-primary">Áp dụng</button>
                <a href="{{ route('destinations.index') }}" class="btn btn-secondary">Xóa bộ lọc</a>
            </div>
        </div>

        <div class="filter-panel-row filter-panel-row--bottom">
            <div class="filter-group filter-group--category">
                <label for="category">Danh mục</label>
                <select name="category_slug" id="category" class="form-control">
                    <option value="">Tất cả</option>
                    @forelse ($categories ?? [] as $cat)
                        <option value="{{ $cat['slug'] ?? '' }}" @if ((request('category_slug') ?? request('category')) == ($cat['slug'] ?? '')) selected @endif>
                            {{ ucfirst($cat['name']) }}
                        </option>
                    @empty
                    @endforelse
                </select>
            </div>

            <div class="filter-group">
                <label for="rating">Đánh giá tối thiểu</label>
                <select name="rating_min" id="rating" class="form-control">
                    <option value="">Tất cả</option>
                    <option value="4.5" @if ((string) (request('rating_min') ?? request('rating')) === '4.5') selected @endif>⭐ 4.5 trở lên</option>
                    <option value="4" @if ((string) (request('rating_min') ?? request('rating')) === '4') selected @endif>⭐ 4 trở lên</option>
                    <option value="3.5" @if ((string) (request('rating_min') ?? request('rating')) === '3.5') selected @endif>⭐ 3.5 trở lên</option>
                </select>
            </div>

            <div class="filter-group">
                <label for="sort">Sắp xếp</label>
                <select name="sort" id="sort" class="form-control">
                    <option value="">Mặc định</option>
                    <option value="rating_desc" @if (request('sort') === 'rating_desc') selected @endif>Đánh giá cao nhất
                    </option>
                    <option value="views_desc" @if (request('sort') === 'views_desc') selected @endif>Lượt xem nhiều nhất
                    </option>
                    <option value="name_asc" @if (request('sort') === 'name_asc') selected @endif>Tên A-Z</option>
                </select>
            </div>
        </div>
    </form>
</div>
