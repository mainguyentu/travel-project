@extends('layouts.app')

@section('title', 'Login - Alats Travel')

@section('content')
    <section class="auth-shell">
        <div class="auth-card panel">
            <h1>Đăng nhập</h1>
            <p class="muted">Tiếp tục hành trình khám phá của bạn.</p>

            @if (session('success'))
                <div class="alert alert-success" role="status">
                    {{ session('success') }}
                </div>
            @endif
            
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
                    <input class="public-input @error('email') is-invalid @enderror" type="email" id="email" name="email"
                        value="{{ old('email') }}" required aria-invalid="@error('email') true @else false @enderror"
                        aria-describedby="email-error">
                    @error('email')
                        <p class="field-error" id="email-error">{{ $message }}</p>
                    @enderror
                </div>

                <div class="form-group">
                    <label for="password">Password</label>
                    <input class="public-input @error('password') is-invalid @enderror" type="password" id="password"
                        name="password" required aria-invalid="@error('password') true @else false @enderror"
                        aria-describedby="password-error">
                    @error('password')
                        <p class="field-error" id="password-error">{{ $message }}</p>
                    @enderror
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
