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

        $errors = [];
        foreach ([$users, $destinations, $topFavorites, $topRatings, $topViews] as $payload) {
            if (($payload['success'] ?? true) === false) {
                $errors[] = $payload['error'] ?? 'Có lỗi khi tải dữ liệu dashboard.';
            }
        }

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
            'stats' => $stats,
            'dashboardErrors' => $errors,
        ]);
    }

    /**
     * Users management
     */
    public function users()
    {
        $response = $this->apiClient->get('admin/users', ['page' => 1, 'limit' => 50]);
        $requestFailed = ($response['success'] ?? true) === false;

        return view('pages.admin.users.index', [
            'users' => $response['data'] ?? [],
            'usersError' => $requestFailed ? ($response['error'] ?? 'Không thể tải danh sách người dùng.') : null,
        ]);
    }

    /**
     * Categories management
     */
    public function categories()
    {
        $response = $this->apiClient->get('admin/categories');
        $requestFailed = ($response['success'] ?? true) === false;

        return view('pages.admin.categories.index', [
            'categories' => $response['data'] ?? [],
            'categoriesError' => $requestFailed ? ($response['error'] ?? 'Không thể tải danh mục.') : null,
        ]);
    }

    /**
     * Destinations management
     */
    public function destinations()
    {
        $response = $this->apiClient->get('admin/destinations', ['page' => 1, 'limit' => 50]);
        $requestFailed = ($response['success'] ?? true) === false;

        return view('pages.admin.destinations.index', [
            'destinations' => $response['data'] ?? [],
            'destinationsError' => $requestFailed ? ($response['error'] ?? 'Không thể tải danh sách điểm đến.') : null,
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

        $errors = [];
        foreach ([$topFavorites, $topRatings, $topViews] as $payload) {
            if (($payload['success'] ?? true) === false) {
                $errors[] = $payload['error'] ?? 'Có lỗi khi tải thống kê.';
            }
        }

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
            'statsErrors' => $errors,
        ]);
    }
}
