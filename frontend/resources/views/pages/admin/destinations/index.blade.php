@extends('layouts.admin')

@section('page-title', 'Destinations Management')

@section('content')
    @php
        $destinationCount = $pagination['total'] ?? [];
        $activeDestinationCount = collect($destinations ?? [])
            ->filter(fn($destination) => ($destination['status'] ?? 'active') === 'active')
            ->count();
        $averageRating =
            collect($destinations ?? [])->avg(fn($destination) => (float) ($destination['rating_avg'] ?? 0)) ?? 0;
        $totalViews = collect($destinations ?? [])->sum(fn($destination) => (int) ($destination['view_count'] ?? 0));
        $currentPage = max((int) ($pagination['current_page'] ?? 1), 1);
        $lastPage = max((int) ($pagination['last_page'] ?? 1), 1);
        $totalDestinationItems = (int) ($pagination['total'] ?? $destinationCount);

        $pageNodes = collect([1, 2, $currentPage - 1, $currentPage, $currentPage + 1, $lastPage - 1, $lastPage])
            ->filter(fn($page) => $page >= 1 && $page <= $lastPage)
            ->unique()
            ->sort()
            ->values();
    @endphp

    <div class="admin-panel-shell admin-page-shell">
        <section class="dashboard-hero admin-page-hero">
            <div class="dashboard-hero-copy">
                <span class="dashboard-eyebrow">Destination catalog</span>
                <h2>Destinations Management</h2>
                <p>Quản lý catalog điểm đến với đầy đủ thông tin mô tả, danh mục, trạng thái và dữ liệu mở rộng.</p>
                <div class="dashboard-quick-links">
                    <a href="#destination-table" class="dashboard-quick-link">Xem danh sách</a>
                    <a href="#destination-create-section" class="dashboard-quick-link"
                        data-open-target="#destination-create-form">Tạo điểm đến</a>
                </div>
            </div>

            <div class="dashboard-hero-panel">
                <div class="dashboard-hero-metric">
                    <span>Total destinations</span>
                    <strong>{{ $destinationCount }}</strong>
                </div>
                <div class="dashboard-hero-metric">
                    <span>Active destinations</span>
                    <strong>{{ $activeDestinationCount }}</strong>
                </div>
                <div class="dashboard-hero-metric">
                    <span>Avg rating / views</span>
                    <strong>{{ number_format((float) $averageRating, 1) }} · {{ number_format($totalViews) }}</strong>
                </div>
            </div>
        </section>

        @if ($categoriesError)
            <div class="alert alert-danger" role="alert">{{ $categoriesError }}</div>
        @endif
        @if ($destinationsError)
            <div class="alert alert-danger" role="alert">{{ $destinationsError }}</div>
        @endif

        <form method="GET" action="{{ route('admin.destinations.index') }}" class="admin-form admin-filter-form">
            <div class="form-group form-group-inline">
                <label for="destination_keyword">Tìm theo tên</label>
                <input id="destination_keyword" name="keyword" type="text" class="form-control"
                    value="{{ $keyword ?? request('keyword') }}" placeholder="Nhập tên địa điểm...">
            </div>
            <div class="admin-edit-actions">
                <button type="submit" class="btn-small">Tìm kiếm</button>
                @if (!empty($keyword ?? request('keyword')))
                    <a href="{{ route('admin.destinations.index') }}" class="btn-small btn-secondary">Xóa lọc</a>
                @endif
            </div>
        </form>

        <div class="admin-table-wrap" id="destination-table">
            <table class="admin-table admin-destinations-table full-width">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Destination</th>
                        <th>Category / Status</th>
                        <th>Insight</th>
                        <th class="col-actions">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse ($destinations as $destination)
                        @php
                            $destinationCategories = collect($destination['categories'] ?? []);
                        @endphp
                        <tr>
                            <td>{{ $destination['id'] }}</td>
                            <td>
                                <div class="admin-destination-main">
                                    <h3 class="admin-destination-title">{{ $destination['name'] }}</h3>
                                    <p class="admin-destination-sub">
                                        {{ $destination['address'] ?? 'Địa chỉ chưa cập nhật' }}</p>
                                    <div class="admin-destination-meta">
                                        <span class="admin-chip admin-chip-muted">ID {{ $destination['id'] }}</span>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <div class="admin-destination-main">
                                    @if ($destinationCategories->isNotEmpty())
                                        <div class="dashboard-pill-stack">
                                            @foreach ($destinationCategories->take(2) as $category)
                                                <span class="dashboard-pill">{{ ucfirst($category['name']) }}</span>
                                            @endforeach
                                            @if ($destinationCategories->count() > 2)
                                                <span
                                                    class="dashboard-pill dashboard-pill-muted">+{{ $destinationCategories->count() - 2 }}</span>
                                            @endif
                                        </div>
                                    @else
                                        <span class="admin-chip admin-chip-muted">No category</span>
                                    @endif

                                    <div class="admin-destination-meta">
                                        <span
                                            class="admin-chip {{ ($destination['status'] ?? 'active') === 'active' ? 'admin-chip-success' : 'admin-chip-warning' }}">
                                            {{ ucfirst($destination['status'] ?? 'active') }}
                                        </span>
                                        <span class="admin-chip admin-chip-muted">
                                            {{ $destination['price_raw_text'] ?? (isset($destination['price_level']) ? ucfirst($destination['price_level']) . ' price' : 'Medium price') }}
                                        </span>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <dl class="admin-destination-stat">
                                    <div class="admin-stat-row">
                                        <dt>Rating</dt>
                                        <dd>{{ number_format((float) ($destination['rating_avg'] ?? 0), 1) }}/5</dd>
                                    </div>
                                    <div class="admin-stat-row">
                                        <dt>Views</dt>
                                        <dd>{{ number_format((int) ($destination['view_count'] ?? 0)) }}</dd>
                                    </div>
                                    <div class="admin-stat-row">
                                        <dt>Open hour</dt>
                                        <dd>{{ $destination['open_hour'] ?? 'N/A' }}</dd>
                                    </div>
                                </dl>
                            </td>
                            <td class="table-actions-cell">
                                <details class="admin-inline-details">
                                    <summary class="btn-small">Chỉnh sửa</summary>
                                    <form method="POST"
                                        action="{{ route('admin.destinations.update', $destination['id']) }}"
                                        class="admin-form admin-edit-form admin-edit-grid">
                                        @csrf
                                        @method('PUT')
                                        <div class="form-group">
                                            <label>Tên</label>
                                            <input id="destination_name_{{ $destination['id'] }}" name="name"
                                                type="text" class="form-control" value="{{ $destination['name'] }}"
                                                data-slug-target="#destination_slug_{{ $destination['id'] }}">
                                        </div>
                                        <div class="form-group">
                                            <label>Slug</label>
                                            <input id="destination_slug_{{ $destination['id'] }}" name="slug"
                                                type="text" class="form-control" value="{{ $destination['slug'] }}">
                                        </div>
                                        <div class="form-group form-group-full">
                                            <label>Danh mục</label>
                                            @php
                                                $selectedCategoryIds = collect($destination['categories'] ?? [])
                                                    ->pluck('id')
                                                    ->all();
                                            @endphp
                                            <div class="dashboard-checkbox-list">
                                                @forelse ($categories as $category)
                                                    <label class="dashboard-checkbox-item">
                                                        <input type="checkbox" name="category_ids[]"
                                                            value="{{ $category['id'] }}" @checked(in_array($category['id'], $selectedCategoryIds, true))>
                                                        <span>{{ $category['name'] }}</span>
                                                    </label>
                                                @empty
                                                    <p class="muted">Chưa có danh mục nào để chọn.</p>
                                                @endforelse
                                            </div>
                                        </div>
                                        <div class="form-group">
                                            <label>Trạng thái</label>
                                            <select name="status" class="form-control">
                                                <option value="active" @selected(($destination['status'] ?? 'active') === 'active')>Active</option>
                                                <option value="inactive" @selected(($destination['status'] ?? 'active') === 'inactive')>Inactive</option>
                                            </select>
                                        </div>
                                        <div class="form-group">
                                            <label>Price level</label>
                                            <select name="price_level" class="form-control">
                                                <option value="low" @selected(($destination['price_level'] ?? 'medium') === 'low')>Low</option>
                                                <option value="medium" @selected(($destination['price_level'] ?? 'medium') === 'medium')>Medium</option>
                                                <option value="high" @selected(($destination['price_level'] ?? 'medium') === 'high')>High</option>
                                            </select>
                                        </div>
                                        <div class="form-group">
                                            <label>Địa chỉ</label>
                                            <input name="address" type="text" class="form-control"
                                                value="{{ $destination['address'] ?? '' }}">
                                        </div>
                                        <div class="form-group">
                                            <label>Giờ mở cửa - đóng cửa</label>
                                            <input name="open_hour" type="text" class="form-control"
                                                value="{{ $destination['open_hour'] ?? '' }}">
                                        </div>
                                        <div class="form-group">
                                            <label>Ảnh đại diện (URL)</label>
                                            <input name="img_url" type="text" class="form-control"
                                                value="{{ $destination['img_url'] ?? '' }}">
                                        </div>
                                        <div class="form-group">
                                            <label>Đường dẫn Maps (URL)</label>
                                            <input name="url_map" type="text" class="form-control"
                                                value="{{ $destination['url_map'] ?? '' }}">
                                        </div>
                                        <div class="form-group">
                                            <label>Latitude (lat)</label>
                                            <input name="lat" type="text" class="form-control"
                                                value="{{ $destination['lat'] ?? '' }}">
                                        </div>
                                        <div class="form-group">
                                            <label>Longitude (lng)</label>
                                            <input name="lng" type="text" class="form-control"
                                                value="{{ $destination['lng'] ?? '' }}">
                                        </div>
                                        <div class="form-group form-group-full">
                                            <label>Mô tả</label>
                                            <textarea name="description" class="form-control" rows="2">{{ $destination['description'] ?? '' }}</textarea>
                                        </div>
                                        <div class="admin-edit-actions">
                                            <button type="submit" class="btn-small">Lưu</button>
                                        </div>
                                    </form>
                                </details>
                                <form method="POST"
                                    action="{{ route('admin.destinations.delete', $destination['id']) }}"
                                    class="d-inline">
                                    @csrf
                                    @method('DELETE')
                                    <button type="submit" class="btn-small btn-danger"
                                        onclick="return confirm('Xoa diem den nay?')">Xoá</button>
                                </form>
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="5">Không có điểm đến để hiển thị.</td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        @if ($lastPage > 1)
            <div class="pagination-wrapper" aria-label="Destination pagination">
                <nav class="pagination">
                    @if ($currentPage > 1)
                        <a href="{{ route('admin.destinations.index', array_merge(request()->except('page'), ['page' => $currentPage - 1])) }}"
                            class="page-link">Prev</a>
                    @else
                        <span class="page-link disabled">Prev</span>
                    @endif

                    @php
                        $previousPrinted = null;
                    @endphp
                    @foreach ($pageNodes as $pageNode)
                        @if ($previousPrinted !== null && $pageNode - $previousPrinted > 1)
                            <span class="page-link dots">...</span>
                        @endif

                        @if ($pageNode === $currentPage)
                            <span class="page-link active">{{ $pageNode }}</span>
                        @else
                            <a href="{{ route('admin.destinations.index', array_merge(request()->except('page'), ['page' => $pageNode])) }}"
                                class="page-link">{{ $pageNode }}</a>
                        @endif

                        @php
                            $previousPrinted = $pageNode;
                        @endphp
                    @endforeach

                    @if ($currentPage < $lastPage)
                        <a href="{{ route('admin.destinations.index', array_merge(request()->except('page'), ['page' => $currentPage + 1])) }}"
                            class="page-link">Next</a>
                    @else
                        <span class="page-link disabled">Next</span>
                    @endif

                </nav>
            </div>
        @endif

        <p class="muted">Tổng số địa điểm: {{ number_format($totalDestinationItems) }}</p>

        <div class="admin-form-wrapper" id="destination-create-section">
            <button type="button" class="btn-secondary admin-form-toggle" data-toggle-target="#destination-create-form"
                data-label-open="Mở form tạo địa điểm" data-label-close="Đóng form tạo địa điểm">Mở form tạo địa
                điểm</button>
            <div id="destination-create-form" class="admin-form-panel" hidden>
                <form method="POST" action="{{ route('admin.destinations.store') }}"
                    class="admin-form admin-form-grid">
                    @csrf
                    <div class="form-group">
                        <label for="destination_name">Tên địa điểm</label>
                        <input id="destination_name" name="name" type="text" class="form-control" required
                            data-slug-target="#destination_slug">
                    </div>
                    <div class="form-group">
                        <label for="destination_slug">Slug</label>
                        <input id="destination_slug" name="slug" type="text" class="form-control" required>
                    </div>
                    <div class="form-group form-group-full">
                        <label>Chọn danh mục</label>
                        <div class="dashboard-checkbox-list">
                            @forelse ($categories as $category)
                                <label class="dashboard-checkbox-item">
                                    <input type="checkbox" name="category_ids[]" value="{{ $category['id'] }}">
                                    <span>{{ $category['name'] }}</span>
                                </label>
                            @empty
                                <p class="muted">Chưa có danh mục nào để chọn.</p>
                            @endforelse
                        </div>
                    </div>
                    <div class="form-group">
                        <label for="destination_status">Trạng thái</label>
                        <select id="destination_status" name="status" class="form-control">
                            <option value="active">Active</option>
                            <option value="inactive">Inactive</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="destination_price">Price level</label>
                        <select id="destination_price" name="price_level" class="form-control">
                            <option value="low">Low</option>
                            <option value="medium" selected>Medium</option>
                            <option value="high">High</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="destination_address">Địa chỉ</label>
                        <input id="destination_address" name="address" type="text" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="destination_open_hour">Giờ mở cửa - đóng cửa</label>
                        <input id="destination_open_hour" name="open_hour" type="text" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="destination_img_url">Ảnh đại diện (URL)</label>
                        <input id="destination_img_url" name="img_url" type="text" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="destination_url_map">Đường dẫn Maps (URL)</label>
                        <input id="destination_url_map" name="url_map" type="text" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="destination_lat">Latitude (lat)</label>
                        <input id="destination_lat" name="lat" type="text" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="destination_lng">Longitude (lng)</label>
                        <input id="destination_lng" name="lng" type="text" class="form-control">
                    </div>
                    <div class="form-group form-group-full">
                        <label for="destination_description">Mô tả</label>
                        <textarea id="destination_description" name="description" class="form-control" rows="3"></textarea>
                    </div>
                    <button type="submit" class="btn-primary">Tạo địa điểm</button>
                </form>
            </div>
        </div>

    </div>
@endsection
