@php($current = request()->route()->getName())
<aside class="sidebar">
    <a href="{{ route('admin.dashboard') }}" class="{{ in_array($current, ['admin.dashboard', 'admin.stats.index']) ? 'active' : '' }}">Dashboard</a>
    <a href="{{ route('admin.users.index') }}" class="{{ str_starts_with($current, 'admin.users') ? 'active' : '' }}">Users</a>
    <a href="{{ route('admin.categories.index') }}" class="{{ str_starts_with($current, 'admin.categories') ? 'active' : '' }}">Categories</a>
    <a href="{{ route('admin.destinations.index') }}" class="{{ str_starts_with($current, 'admin.destinations') ? 'active' : '' }}">Destinations</a>
    <a href="{{ route('admin.audit-logs.index') }}" class="{{ str_starts_with($current, 'admin.audit-logs') ? 'active' : '' }}">Audit logs</a>
</aside>
