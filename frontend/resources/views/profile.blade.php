@extends('layouts.public')

@section('title', 'Hồ sơ')

@section('content')
<div class="container">
    <div class="form-card">
        <h1>Hồ sơ</h1>
        <p>Email: <strong>{{ $user['email'] ?? '' }}</strong></p>
        <p><a class="btn" href="{{ route('favorites.index') }}">Địa điểm yêu thích của tôi</a></p>
    </div>
</div>
@endsection
