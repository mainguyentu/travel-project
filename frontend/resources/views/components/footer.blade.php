<footer class="site-footer">
    <div class="site-container">
        <div class="site-footer-grid">
            <div>
                <div class="footer-brand-row">
                    <span class="footer-brand-icon">✦</span>
                    <div>
                        <h3 class="footer-brand-title">Alats Travel</h3>
                        <p class="footer-brand-subtitle">Atlas du lịch</p>
                    </div>
                </div>
                <p>
                    Hướng dẫn du lịch toàn diện cho thành phố Đà Nẵng - Điểm đến hấp dẫn nhất Việt Nam.
                </p>
                <div class="social-links">
                    <a href="#" class="social-link" aria-label="Facebook">F</a>
                    <a href="#" class="social-link" aria-label="Instagram">I</a>
                    <a href="#" class="social-link" aria-label="Youtube">Y</a>
                </div>
            </div>

            <div>
                <h4>Liên kết nhanh</h4>
                <ul>
                    <li><a href="{{ route('home') }}">Trang chủ</a></li>
                    <li><a href="{{ route('destinations.index') }}">Điểm đến</a></li>
                    <li><a href="{{ route('favorites.index') }}">Yêu thích</a></li>
                    <li><a href="{{ route('profile.index') }}">Tài khoản</a></li>
                </ul>
            </div>

            <div>
                <h4>Kham pha</h4>
                <ul>
                    <li><a href="{{ route('destinations.index', ['price_level' => 1]) }}">Điểm đến tiết kiệm</a></li>
                    <li><a href="{{ route('destinations.index', ['rating' => 4.5]) }}">Đánh giá cao</a></li>
                    <li><a href="{{ route('destinations.index', ['price_level' => 3]) }}">Trải nghiệm cao cấp</a></li>
                </ul>
            </div>

            <div>
                <h4>Liên hệ</h4>
                <p>Email: contact@alats.travel</p>
                <p>Đà Nẵng, Việt Nam</p>
            </div>
        </div>

        <div class="site-footer-bottom">
            <p>&copy; 2026 Đà Nẵng Atlas Du lịch. Thiết kế với ❤️ cho thành phố đáng sống.</p>
        </div>
    </div>
</footer>
