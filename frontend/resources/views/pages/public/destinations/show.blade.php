@extends('layouts.app')

@section('title', $destination['name'] ?? 'Destination')

@section('content')
    <section class="public-shell">
        <div class="site-container detail-layout">
            <section class="detail-hero">
                @dd($destination)
                @if ($destination['img_url'] ?? null)
                    <img src="{{ $destination['img_url'] }}" alt="{{ $destination['name'] }}">
                @endif
                <div class="detail-overlay">
                    <div>
                        <span class="badge badge-soft" style="background:rgba(255,255,255,0.86); color:#0f172a;">
                            {{ $destination['categories'][0]['name'] ?? 'Diem den' }}
                        </span>
                        <h1 style="margin:0.55rem 0 0.35rem; font-size:clamp(1.8rem,3.5vw,3rem);">{{ $destination['name'] ?? 'N/A' }}</h1>
                        <p style="margin:0; color:rgba(255,255,255,0.9);">
                            Đánh giá {{ number_format((float) ($destination['rating_avg'] ?? 0), 1) }}/5 ·
                            {{ $destination['review_count'] ?? 0 }} reviews ·
                            {{ str_repeat('$', $destination['price_level'] ?? 1) }}
                        </p>
                    </div>
                </div>
            </section>

            <section class="detail-content">
                <article class="detail-panel panel">
                    <h2>Thông tin tổng quan</h2>
                    <p class="muted">{{ $destination['description'] ?? 'Chưa có mô tả cho địa chỉ này.' }}</p>

                    <div class="meta-grid" style="margin-top:0.8rem;">
                        <div class="public-card" style="padding:0.8rem;">
                            <strong>Danh mục</strong>
                            <p class="muted" style="margin:0.35rem 0 0;">{{ $destination['categories'][0]['name'] ?? 'N/A' }}</p>
                        </div>
                        <div class="public-card" style="padding:0.8rem;">
                            <strong>Địa chỉ</strong>
                            <p class="muted" style="margin:0.35rem 0 0;">{{ $destination['address'] ?? 'Chưa cập nhật' }}</p>
                        </div>
                        <div class="public-card" style="padding:0.8rem;">
                            <strong>Mức giá</strong>
                            <p class="muted" style="margin:0.35rem 0 0;">{{ str_repeat('$', $destination['price_level'] ?? 1) }}</p>
                        </div>
                    </div>
                </article>

                @if ($destination['url_map'] ?? null)
                    <article class="detail-panel panel">
                        <h2>Bản đồ</h2>
                        <iframe
                            src="{{ $destination['url_map'] }}"
                            loading="lazy"
                            referrerpolicy="no-referrer-when-downgrade"
                            style="width:100%;height:360px;border:0;border-radius:14px;"
                            title="Map of {{ $destination['name'] }}"
                        ></iframe>
                    </article>
                @endif

                <article class="detail-panel panel">
                    <h2>Tương tác</h2>
                    @if (session()->has('access_token'))
                        <button class="btn-primary" data-id="{{ $destination['id'] }}">❤ Lưu vào yêu thích</button>
                    @else
                        <a href="{{ route('login') }}" class="btn-primary">Đăng nhập để lưu yêu thích</a>
                    @endif
                </article>

                @if (session()->has('access_token'))
                    <article class="detail-panel panel">
                        <h3>Gửi đánh giá</h3>
                        <form action="{{ route('ratings.store', $destination['id']) }}" method="POST">
                            @csrf
                            @method('PUT')

                            <div class="form-group">
                                <label for="rating">Số sao</label>
                                <select name="rating_score" id="rating" class="public-select" required>
                                    <option value="">Chọn số sao</option>
                                    @for ($i = 5; $i >= 1; $i--)
                                        <option value="{{ $i }}">{{ $i }} sao</option>
                                    @endfor
                                </select>
                            </div>

                            <div class="form-group">
                                <label for="comment">Nhận xét</label>
                                <textarea name="comment" id="comment" rows="4" class="public-textarea" placeholder="Chia se trai nghiem cua ban..."></textarea>
                            </div>

                            <button type="submit" class="btn-primary">Gửi đánh giá</button>
                        </form>
                    </article>
                @else
                    <article class="detail-panel panel">
                        <p>Vui lòng <a href="{{ route('login') }}" style="color:#0e7490;font-weight:700;">đăng nhập</a> để gửi đánh giá.</p>
                    </article>
                @endif
            </section>
        </div>
    </section>
@endsection
