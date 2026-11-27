<footer class="footer">
    <div class="footer-inner">
        <div>
            <h4>Đà Nẵng Atlas Du lịch</h4>
            <p>Hướng dẫn du lịch toàn diện cho thành phố Đà Nẵng — điểm đến hấp dẫn nhất Việt Nam.</p>
        </div>
        <div>
            <h4>Liên kết nhanh</h4>
            <ul>
                <li><a href="{{ route('home') }}">Trang chủ</a></li>
                <li><a href="{{ route('destinations.index') }}">Điểm đến</a></li>
                @auth
                @endauth
                @if (session('access_token'))
                    <li><a href="{{ route('favorites.index') }}">Yêu thích</a></li>
                @else
                    <li><a href="{{ route('login') }}">Đăng nhập</a></li>
                @endif
            </ul>
        </div>
        <div>
            <h4>Khám phá</h4>
            <ul>
                <li><a href="{{ route('destinations.index') }}">Tất cả địa điểm</a></li>
                <li><a href="{{ route('destinations.index', ['sort' => 'rating']) }}">Rating cao</a></li>
                <li><a href="{{ route('destinations.index', ['sort' => 'views']) }}">Xem nhiều</a></li>
            </ul>
        </div>
        <div>
            <h4>Liên hệ</h4>
            <ul>
                <li>+84 236 123 4567</li>
                <li>info@danang-atlas.vn</li>
                <li>Đà Nẵng, Việt Nam</li>
            </ul>
        </div>
    </div>
    <div class="footer-bottom">
        <p>&copy; 2026 Đà Nẵng Atlas Du lịch — Alats Travel.</p>
    </div>
</footer>
