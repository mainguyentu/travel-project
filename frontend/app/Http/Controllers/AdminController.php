<?php

namespace App\Http\Controllers;

use App\Services\ApiClient;

class AdminController extends Controller
{
    private ApiClient $apiClient;

    public function __construct(ApiClient $apiClient)
    {
        $this->apiClient = $apiClient;
    }

    /**
     * Dashboard
     */
    public function dashboard()
    {
        $users = $this->apiClient->get('admin/users', ['page' => 1, 'limit' => 1]);
        $destinations = $this->apiClient->get('admin/destinations', ['page' => 1, 'limit' => 1]);
        $topFavorites = $this->apiClient->get('admin/stats/top-favorites');
        $topRatings = $this->apiClient->get('admin/stats/top-ratings');
        $topViews = $this->apiClient->get('admin/stats/top-views');

        $stats = [
            'total_users' => (int) (($users['meta']['total'] ?? 0)),
            'total_destinations' => (int) (($destinations['meta']['total'] ?? 0)),
            'total_reviews' => 0,
            'avg_rating' => 0,
            'top_favorites' => $topFavorites['data'] ?? [],
            'top_ratings' => $topRatings['data'] ?? [],
            'top_views' => $topViews['data'] ?? [],
        ];
        
        return view('pages.admin.dashboard', [
            'stats' => $stats['data'] ?? [],
        ]);
    }

    /**
     * Users management
     */
    public function users()
    {
        $response = $this->apiClient->get('admin/users', ['page' => 1, 'limit' => 50]);

        return view('pages.admin.users.index', [
            'users' => $response['data'] ?? [],
        ]);
    }

    /**
     * Categories management
     */
    public function categories()
    {
        $response = $this->apiClient->get('admin/categories');

        return view('pages.admin.categories.index', [
            'categories' => $response['data'] ?? [],
        ]);
    }

    /**
     * Destinations management
     */
    public function destinations()
    {
        $response = $this->apiClient->get('admin/destinations', ['page' => 1, 'limit' => 50]);

        return view('pages.admin.destinations.index', [
            'destinations' => $response['data'] ?? [],
        ]);
    }

    /**
     * Statistics
     */
    public function stats()
    {
        $topFavorites = $this->apiClient->get('admin/stats/top-favorites');
        $topRatings = $this->apiClient->get('admin/stats/top-ratings');
        $topViews = $this->apiClient->get('admin/stats/top-views');

        $response = [
            'data' => [
                'top_favorites' => $topFavorites['data'] ?? [],
                'top_ratings' => $topRatings['data'] ?? [],
                'top_views' => $topViews['data'] ?? [],
                'total_requests' => 0,
                'unique_users' => 0,
                'avg_response_time' => 0,
                'error_rate' => 0,
                'new_users_today' => 0,
                'new_reviews_today' => 0,
                'active_sessions' => 0,
            ],
        ];

        return view('pages.admin.stats', [
            'stats' => $response['data'] ?? [],
        ]);
    }
}
