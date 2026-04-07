<?php

namespace App\Http\Controllers;

use App\Services\ApiClient;
use Illuminate\Http\Request;

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
        $categoriesResponse = $this->apiClient->get('admin/categories');
        $requestFailed = ($response['success'] ?? true) === false;
        $categoriesFailed = ($categoriesResponse['success'] ?? true) === false;

        return view('pages.admin.destinations.index', [
            'destinations' => $response['data'] ?? [],
            'destinationsError' => $requestFailed ? ($response['error'] ?? 'Không thể tải danh sách điểm đến.') : null,
            'categories' => $categoriesResponse['data'] ?? [],
            'categoriesError' => $categoriesFailed ? ($categoriesResponse['error'] ?? 'Khong the tai danh muc.') : null,
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

    /**
     * Update user status
     */
    public function updateUserStatus(Request $request, int $userId)
    {
        $validated = $request->validate([
            'status' => 'required|in:active,locked',
        ]);

        $response = $this->apiClient->patch("admin/users/{$userId}/status", $validated);

        return $this->handleActionResponse(
            $response,
            'Không thể cập nhật trạng thái người dùng.',
            'Đã cập nhật trạng thái người dùng.'
        );
    }

    /**
     * Update user role
     */
    public function updateUserRole(Request $request, int $userId)
    {
        $validated = $request->validate([
            'role' => 'required|in:user,admin',
        ]);

        $response = $this->apiClient->patch("admin/users/{$userId}/role", $validated);

        return $this->handleActionResponse(
            $response,
            'Không thể cập nhật quyền người dùng',
            'Đã cập nhật quyền người dùng.'
        );
    }

    /**
     * Create category
     */
    public function createCategory(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:120',
            'slug' => 'required|string|max:160',
            'descriptions' => 'nullable|string',
        ]);

        $response = $this->apiClient->post('admin/categories', $validated);

        return $this->handleActionResponse(
            $response,
            'Không thể tạo danh mục.',
            'Đã tạo danh mục mới.'
        );
    }

    /**
     * Update category
     */
    public function updateCategory(Request $request, int $categoryId)
    {
        $validated = $request->validate([
            'name' => 'nullable|string|max:120',
            'slug' => 'nullable|string|max:160',
            'descriptions' => 'nullable|string',
        ]);

        $payload = array_filter($validated, fn ($value) => $value !== null && $value !== '');
        if ($payload === []) {
            return back()->withErrors(['admin' => 'Vui lòng nhập ít nhất 1 trường cần cập nhật']);
        }

        $response = $this->apiClient->put("admin/categories/{$categoryId}", $payload);

        return $this->handleActionResponse(
            $response,
            'Không thể cập nhật danh mục.',
            'Đã cập nhật danh mục.'
        );
    }

    /**
     * Delete category
     */
    public function deleteCategory(int $categoryId)
    {
        $response = $this->apiClient->delete("admin/categories/{$categoryId}");

        return $this->handleActionResponse(
            $response,
            'Không thể xoá danh mục.',
            'Đã xoá danh mục.'
        );
    }

    /**
     * Create destination
     */
    public function createDestination(Request $request)
    {
        $validated = $request->validate([
            'name' => 'required|string|max:180',
            'slug' => 'required|string|max:220',
            'address' => 'nullable|string',
            'description' => 'nullable|string',
            'price_level' => 'nullable|in:low,medium,high',
            'open_hour' => 'nullable|string',
            'img_url' => 'nullable|string',
            'url_map' => 'nullable|string',
            'lat' => 'nullable|numeric',
            'lng' => 'nullable|numeric',
            'status' => 'nullable|in:active,inactive',
            'category_ids' => 'nullable',
        ]);

        $payload = $this->buildDestinationPayload($validated, $request);
        $response = $this->apiClient->post('admin/destinations', $payload);

        return $this->handleActionResponse(
            $response,
            'Không thể tạo mới địa điểm.',
            'Đã tạo địa điểm mới.'
        );
    }

    /**
     * Update destination
     */
    public function updateDestination(Request $request, int $destinationId)
    {
        $validated = $request->validate([
            'name' => 'nullable|string|max:180',
            'slug' => 'nullable|string|max:220',
            'address' => 'nullable|string',
            'description' => 'nullable|string',
            'price_level' => 'nullable|in:low,medium,high',
            'open_hour' => 'nullable|string',
            'img_url' => 'nullable|string',
            'url_map' => 'nullable|string',
            'lat' => 'nullable|numeric',
            'lng' => 'nullable|numeric',
            'status' => 'nullable|in:active,inactive',
            'category_ids' => 'nullable',
        ]);

        $payload = $this->buildDestinationPayload($validated, $request);
        if ($payload === []) {
            return back()->withErrors(['admin' => 'Vui lòng nhập ít nhất 1 trường cần cập nhật.']);
        }

        $response = $this->apiClient->put("admin/destinations/{$destinationId}", $payload);

        return $this->handleActionResponse(
            $response,
            'Không thể cập nhật địa điểm.',
            'Đã câp nhật địa điểm.'
        );
    }

    /**
     * Delete destination
     */
    public function deleteDestination(int $destinationId)
    {
        $response = $this->apiClient->delete("admin/destinations/{$destinationId}");

        return $this->handleActionResponse(
            $response,
            'Không thể xoá địa điểm.',
            'Đã xoá địa điểm.'
        );
    }

    private function handleActionResponse(array $response, string $fallbackError, string $successMessage)
    {
        if (request()->wantsJson()) {
            return response()->json($response);
        }

        if (($response['success'] ?? false) === false) {
            return back()->withErrors(['admin' => $response['error'] ?? $fallbackError])->withInput();
        }

        return back()->with('success', $successMessage);
    }

    private function buildDestinationPayload(array $validated, Request $request): array
    {
        $payload = [
            'name' => $validated['name'] ?? null,
            'slug' => $validated['slug'] ?? null,
            'address' => $validated['address'] ?? null,
            'description' => $validated['description'] ?? null,
            'price_level' => $validated['price_level'] ?? null,
            'open_hour' => $validated['open_hour'] ?? null,
            'img_url' => $validated['img_url'] ?? null,
            'url_map' => $validated['url_map'] ?? null,
            'lat' => $this->normalizeNumber($validated['lat'] ?? null),
            'lng' => $this->normalizeNumber($validated['lng'] ?? null),
            'status' => $validated['status'] ?? null,
        ];

        $categoryIds = $this->parseCategoryIds($request->input('category_ids'));
        if ($categoryIds !== null) {
            $payload['category_ids'] = $categoryIds;
        }

        return array_filter($payload, fn ($value) => $value !== null && $value !== '');
    }

    private function parseCategoryIds($raw): ?array
    {
        if ($raw === null) {
            return null;
        }

        if (is_array($raw)) {
            $ids = array_filter($raw, fn ($value) => is_numeric($value));
            return array_map('intval', $ids);
        }

        if (is_string($raw)) {
            $parts = preg_split('/[,\s]+/', $raw, -1, PREG_SPLIT_NO_EMPTY);
            $ids = array_filter($parts, fn ($value) => is_numeric($value));
            return array_map('intval', $ids);
        }

        return null;
    }

    private function normalizeNumber($value): ?float
    {
        if ($value === null || $value === '') {
            return null;
        }

        return (float) $value;
    }
}
