<!DOCTYPE html>
<html lang="vi" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'Alats Travel Đà Nẵng')</title>
    <link rel="stylesheet" href="{{ asset('css/app.css') }}">
    <script>
        try {
            var t = localStorage.getItem('alats-theme') || 'light';
            document.documentElement.setAttribute('data-theme', t);
        } catch (e) {}
    </script>
</head>
<body>
    <a class="skip-link" href="#main-content">Bỏ qua tới nội dung chính</a>
    <x-navbar />
    @if (session('status') || session('error'))
        <x-alert type="{{ session('error') ? 'error' : 'success' }}" message="{{ session('error') ?? session('status') }}" />
    @endif
    <main id="main-content">
    @yield('content')
    </main>
    <x-footer />
    <script>
        function toggleTheme() {
            var el = document.documentElement;
            var next = el.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            el.setAttribute('data-theme', next);
            try { localStorage.setItem('alats-theme', next); } catch (e) {}
        }
    </script>
    <script src="{{ asset('js/app.js') }}"></script>
    @stack('scripts')
</body>
</html>
