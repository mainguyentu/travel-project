<!DOCTYPE html>
<html lang="vi" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@yield('title', 'Admin — Alats Travel')</title>
    <link rel="stylesheet" href="{{ asset('css/app.css') }}">
    <script>
        try {
            var t = localStorage.getItem('alats-theme') || 'light';
            document.documentElement.setAttribute('data-theme', t);
        } catch (e) {}
    </script>
</head>
<body class="admin">
    <x-admin-topbar />
    <div class="admin-shell">
        <x-admin-sidebar />
        <main class="admin-main">
            @if (session('status') || session('error'))
                <x-alert type="{{ session('error') ? 'error' : 'success' }}" message="{{ session('error') ?? session('status') }}" />
            @endif
            @yield('content')
        </main>
    </div>
    <script>
        function toggleTheme() {
            var el = document.documentElement;
            var next = el.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            el.setAttribute('data-theme', next);
            try { localStorage.setItem('alats-theme', next); } catch (e) {}
        }
    </script>
</body>
</html>
