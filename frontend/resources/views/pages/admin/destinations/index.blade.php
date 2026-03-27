@extends('layouts.admin')

@section('page-title', 'Destinations Management')

@section('content')
    <div class="admin-section">
        <div class="section-header">
            <h2>Destinations Management</h2>
            <a href="#" class="btn-primary">Add Destination</a>
        </div>

        <table class="admin-table full-width">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Slug</th>
                    <th>Category</th>
                    <th>Rating</th>
                    <th>Views</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                @forelse ($destinations as $destination)
                    <tr>
                        <td>{{ $destination['id'] }}</td>
                        <td>{{ $destination['name'] }}</td>
                        <td><code>{{ $destination['slug'] }}</code></td>
                        <td>{{ $destination['categories'][0]['name'] ?? 'N/A' }}</td>
                        <td>
                            <span class="rating">
                                {{ $destination['rating_avg'] ?? 0 }}/5 ⭐
                            </span>
                        </td>
                        <td>{{ $destination['view_count'] ?? 0 }}</td>
                        <td>
                            <div class="actions">
                                <a href="{{ route('destinations.show', $destination['id']) }}" class="btn-small">View</a>
                                <a href="#" class="btn-small">Edit</a>
                                <button class="btn-small btn-danger" data-destination-id="{{ $destination['id'] }}">Delete</button>
                            </div>
                        </td>
                    </tr>
                @empty
                    <tr><td colspan="7">No destinations found</td></tr>
                @endforelse
            </tbody>
        </table>
    </div>
@endsection

@push('styles')
    <style>
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .full-width {
            width: 100%;
        }

        .rating {
            color: #f59e0b;
            font-weight: bold;
        }

        .actions {
            display: flex;
            gap: 0.5rem;
        }

        .btn-small {
            padding: 0.5rem 1rem;
            font-size: 0.875rem;
        }

        code {
            background: #f5f5f5;
            padding: 0.25rem 0.5rem;
            border-radius: 3px;
        }
    </style>
@endpush
