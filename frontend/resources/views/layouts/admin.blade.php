<!DOCTYPE html>
<html lang="{{ str_replace('_', '-', app()->getLocale()) }}">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title') - Admin</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="admin-layout">
    <div class="admin-wrapper">
        <!-- Sidebar Navigation -->
        <aside class="admin-sidebar">
            @include('components.admin-sidebar')
        </aside>

        <!-- Main Content -->
        <section class="admin-content">
            <!-- Topbar -->
            @include('components.admin-topbar')

            <!-- Page Content -->
            <div class="admin-page">
                @if ($errors->any())
                    @include('components.alert', ['type' => 'danger', 'title' => 'Lỗi', 'messages' => $errors->all()])
                @endif

                @if (session('success'))
                    @include('components.alert', ['type' => 'success', 'title' => 'Thành công', 'message' => session('success')])
                @endif

                @yield('content')
            </div>
        </section>
    </div>

    @stack('scripts')
</body>
</html>
