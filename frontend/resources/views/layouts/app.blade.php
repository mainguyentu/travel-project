<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title') - Alats Travel</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="public-body">
    <div class="site-shell">
        @include('components.navbar')

        <main class="public-main">
            @yield('content')
        </main>

        @include('components.footer')
    </div>

    @stack('scripts')
</body>
</html>
