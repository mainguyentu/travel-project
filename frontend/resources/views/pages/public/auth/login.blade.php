@extends('layouts.app')

@section('title', 'Login - Alats Travel')

@section('content')
    <section class="auth-shell">
        <div class="auth-card panel">
            <h1>Đăng nhập</h1>
            <p class="muted">Tiếp tục hành trình khám phá của bạn.</p>
            
            @if ($errors->any())
                <div class="alert alert-error" role="alert">
                    <ul>
                        @foreach ($errors->all() as $error)
                            <li>{{ $error }}</li>
                        @endforeach
                    </ul>
                </div>
            @endif

            <form action="{{ route('login') }}" method="POST" class="auth-form">
                @csrf

                <div class="form-group">
                    <label for="email">Email</label>
                    <input class="public-input" type="email" id="email" name="email" value="{{ old('email') }}" required>
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input class="public-input" type="password" id="password" name="password" required>
                </div>

                <button type="submit" class="btn-primary btn-block">Đăng nhập</button>
            </form>

            <p class="muted auth-switch-text">
                Bạn chưa có tài khoản?
                <a href="{{ route('register') }}" class="auth-switch-link">Đăng ký ngay</a>
            </p>
        </div>
    </section>
@endsection
