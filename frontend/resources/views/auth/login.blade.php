@extends('layouts.public')

@section('title', 'Đăng nhập')

@section('content')
<div class="container">
    <div class="form-card">
        <h1>Đăng nhập</h1>
        <form method="POST" action="{{ route('login') }}">
            @csrf
            <label for="email">Email</label>
            <input id="email" type="email" name="email" value="{{ old('email') }}" required>
            @error('email')<p class="field-error">{{ $message }}</p>@enderror
            <label for="password">Mật khẩu</label>
            <input id="password" type="password" name="password" required>
            @error('password')<p class="field-error">{{ $message }}</p>@enderror
            <button type="submit" style="width:100%;margin-top:1rem">Đăng nhập</button>
        </form>
        <p class="muted" style="text-align:center">Chưa có tài khoản? <a href="{{ route('register') }}">Đăng ký</a></p>
    </div>
</div>
@endsection
