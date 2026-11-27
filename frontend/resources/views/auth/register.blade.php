@extends('layouts.public')

@section('title', 'Đăng ký')

@section('content')
<div class="container">
    <div class="form-card">
        <h1>Đăng ký</h1>
        <form method="POST" action="{{ route('register') }}">
            @csrf
            <label for="name">Tên</label>
            <input id="name" type="text" name="name" value="{{ old('name') }}" required maxlength="120">
            @error('name')<p class="field-error">{{ $message }}</p>@enderror
            <label for="email">Email</label>
            <input id="email" type="email" name="email" value="{{ old('email') }}" required>
            @error('email')<p class="field-error">{{ $message }}</p>@enderror
            <label for="password">Mật khẩu</label>
            <input id="password" type="password" name="password" required>
            @error('password')<p class="field-error">{{ $message }}</p>@enderror
            <label for="password_confirmation">Nhập lại mật khẩu</label>
            <input id="password_confirmation" type="password" name="password_confirmation" required>
            <button type="submit" style="width:100%;margin-top:1rem">Đăng ký</button>
        </form>
    </div>
</div>
@endsection
