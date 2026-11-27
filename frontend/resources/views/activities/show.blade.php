@extends('layouts.app')

@section('title', ($payload['activity']['name'] ?? 'Activity').' — Gợi ý')

@section('content')
<h1>{{ $payload['activity']['name'] ?? 'Activity' }}</h1>
@if (! empty($payload['recommended_destinations']))
<section>
    <h2>Địa điểm gợi ý</h2>
    <div class="grid">
        @foreach ($payload['recommended_destinations'] as $d)
            <article class="card">
                <h3>{{ $d['name'] }}</h3>
                <p class="muted">{{ $d['address'] ?? '' }}</p>
                <p>Rating: {{ $d['rating_avg'] ?? 0 }}</p>
            </article>
        @endforeach
    </div>
</section>
@endif
@if (! empty($payload['trending']))
<section>
    <h2>Đang thịnh hành</h2>
    <ul>
        @foreach ($payload['trending'] as $d)
            <li>{{ $d['name'] }}</li>
        @endforeach
    </ul>
</section>
@endif
@endsection
