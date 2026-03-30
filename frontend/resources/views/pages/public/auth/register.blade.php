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
                    <input class="public-input @error('name') is-invalid @enderror" type="text" id="name" name="name"
                        value="{{ old('name') }}" required aria-invalid="@error('name') true @else false @enderror"
                        aria-describedby="name-error">
                    @error('name')
                        <p class="field-error" id="name-error">{{ $message }}</p>
                    @enderror
                </div>

                <div class="form-group">
                    <label for="email">Email</label>
                    <input class="public-input @error('email') is-invalid @enderror" type="email" id="email"
                        name="email" value="{{ old('email') }}" required
                        aria-invalid="@error('email') true @else false @enderror" aria-describedby="email-error">
                    @error('email')
                        <p class="field-error" id="email-error">{{ $message }}</p>
                    @enderror
                </div>

                <div class="form-group">
                    <label for="password">Mật khẩu</label>
                    <input class="public-input @error('password') is-invalid @enderror" type="password" id="password"
                        name="password" required aria-invalid="@error('password') true @else false @enderror"
                        aria-describedby="password-error">
                    @error('password')
                        <p class="field-error" id="password-error">{{ $message }}</p>
                    @enderror
                </div>

                <div class="form-group">
                    <label for="password_confirmation">Xác nhận mật khẩu</label>
                    <input class="public-input @error('password_confirmation') is-invalid @enderror" type="password"
                        id="password_confirmation" name="password_confirmation" required
                        aria-invalid="@error('password_confirmation') true @else false @enderror"
                        aria-describedby="password-confirmation-error">
                    @error('password_confirmation')
                        <p class="field-error" id="password-confirmation-error">{{ $message }}</p>
                    @enderror
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
