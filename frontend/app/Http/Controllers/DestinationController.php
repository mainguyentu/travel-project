<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class DestinationController extends BaseController
{
    public function index(Request $request)
    {
        $query = $request->only(['category_slug', 'price_level', 'rating_min', 'keyword', 'sort', 'q']);
        $query['page'] = max(1, (int) $request->input('page', 1));
        $query['limit'] = 15;

        $path = $request->filled('q') ? 'destinations/search' : 'destinations';
        $body = $this->api()->get($path, array_filter($query, fn ($v) => $v !== null && $v !== ''));
        $filters = $this->api()->get('public/landing');

        return view('destinations.index', [
            'destinations' => $body['data'] ?? [],
            'meta' => $body['meta'] ?? ['page' => 1, 'limit' => 15, 'total' => 0],
            'filters' => $filters['data']['categories'] ?? [],
            'query' => $request->only(['category_slug', 'price_level', 'rating_min', 'keyword', 'sort']),
            'favoriteIds' => $this->favoriteIds(),
        ]);
    }
}
