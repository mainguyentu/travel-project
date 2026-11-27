@extends('layouts.admin')

@section('title', 'Audit logs')

@section('content')
<div class="page-head"><div><h1>Audit logs</h1><p class="muted">Tổng {{ $meta['total'] ?? 0 }}</p></div></div>
<table class="admin-table">
    <thead><tr><th>ID</th><th>Actor</th><th>Action</th><th>Entity</th><th>Detail</th><th>Thời gian</th></tr></thead>
    <tbody>
    @foreach ($logs as $log)
        @php
            $badge = str_contains($log['action'], 'delete') ? 'badge-locked'
                : (str_contains($log['action'], 'create') ? 'badge-ok'
                : (str_contains($log['action'], 'update') ? 'badge-info' : 'badge-warn'));
        @endphp
        <tr>
            <td>{{ $log['id'] }}</td>
            <td>{{ $log['actor_user_id'] ?? '—' }}</td>
            <td><span class="badge {{ $badge }}">{{ $log['action'] }}</span></td>
            <td>{{ $log['entity'] }} {{ $log['entity_id'] ?? '' }}</td>
            <td>
                <details><summary>Xem</summary>{{ json_encode($log['detail'] ?? [], JSON_UNESCAPED_UNICODE) }}</details>
            </td>
            <td class="muted">{{ $log['created_at'] ?? '' }}</td>
        </tr>
    @endforeach
    </tbody>
</table>
@endsection
