<div class="filter-panel">
    <h3>Bộ Lọc</h3>

    <form method="GET" action="{{ route('destinations.index') }}" id="filterForm">
        <!-- Category Filter -->
        <div class="filter-group">
            <label for="category">Danh Mục</label>
            <select name="category_slug" id="category" class="form-control">
                <option value="">Tất Cả</option>
                @forelse ($categories ?? [] as $cat)
                    <option value="{{ $cat['slug'] ?? '' }}" @if((request('category_slug') ?? request('category')) == ($cat['slug'] ?? '')) selected @endif>
                        {{ $cat['name'] }}
                    </option>
                @empty
                @endforelse
            </select>
        </div>

        <!-- Price Level Filter -->
        <div class="filter-group">
            <label for="priceLevel">Mức Giá</label>
            <select name="price_level" id="priceLevel" class="form-control">
                <option value="">Tất Cả</option>
                <option value="1" @if(request('price_level') == 1) selected @endif>$ - Rẻ</option>
                <option value="2" @if(request('price_level') == 2) selected @endif>$$ - Vừa</option>
                <option value="3" @if(request('price_level') == 3) selected @endif>$$$ - Đắt</option>
                <option value="4" @if(request('price_level') == 4) selected @endif>$$$$ - Rất Đắt</option>
            </select>
        </div>

        <!-- Rating Filter -->
        <div class="filter-group">
            <label for="rating">Đánh Giá Tối Thiểu</label>
            <select name="rating_min" id="rating" class="form-control">
                <option value="">Tất Cả</option>
                <option value="1" @if((request('rating_min') ?? request('min_rating')) == 1) selected @endif>⭐ 1 sao trở lên</option>
                <option value="2" @if((request('rating_min') ?? request('min_rating')) == 2) selected @endif>⭐ 2 sao trở lên</option>
                <option value="3" @if((request('rating_min') ?? request('min_rating')) == 3) selected @endif>⭐ 3 sao trở lên</option>
                <option value="4" @if((request('rating_min') ?? request('min_rating')) == 4) selected @endif>⭐ 4 sao trở lên</option>
            </select>
        </div>

        <!-- Search -->
        <div class="filter-group">
            <label for="search">Tìm Kiếm</label>
             <input type="text" name="keyword" id="search" class="form-control" 
                 placeholder="Tên địa điểm..." value="{{ request('keyword', request('search')) }}">
        </div>

        <div class="filter-buttons">
            <button type="submit" class="btn btn-primary">Tìm Kiếm</button>
            <a href="{{ route('destinations.index') }}" class="btn btn-secondary">Xóa Bộ Lọc</a>
        </div>
    </form>
</div>

