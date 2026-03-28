@extends('layouts.app')

@section('title', 'Register - Alats Travel')

@section('content')
    <section class="auth-shell">
        <div class="auth-card panel">
            <h1>Tạo tài khoản</h1>
            <p class="muted">Đăng ký và khám phá thêm nhiều hơn.</p>
            
            @if ($errors->any())
                <div class="alert alert-error" role="alert">
                    <ul>
                        @foreach ($errors->all() as $error)
                            <li>{{ $error }}</li>
                        @endforeach
                    </ul>
                </div>
            @endif

            <form action="{{ route('register') }}" method="POST" class="auth-form">
                @csrf

                <div class="form-group">
                    <label for="name">Họ tên</label>
                    <input class="public-input" type="text" id="name" name="name" value="{{ old('name') }}" required>
                </div>

                <div class="form-group">
                    <label for="email">Email</label>
                    <input class="public-input" type="email" id="email" name="email" value="{{ old('email') }}" required>
                </div>

                <div class="form-group">
                    <label for="password">Mật khẩu</label>
                    <input class="public-input" type="password" id="password" name="password" required>
                </div>

                <div class="form-group">
                    <label for="password_confirmation">Xác nhận mật khẩu</label>
                    <input class="public-input" type="password" id="password_confirmation" name="password_confirmation" required>
                </div>

                <button type="submit" class="btn-primary btn-block">Đăng ký</button>
            </form>

            <p class="muted auth-switch-text">
                Bạn đã có tài khoản?
                <a href="{{ route('login') }}" class="auth-switch-link">Đăng nhập ngay</a>
            </p>
        </div>
    </section>
@endsection
