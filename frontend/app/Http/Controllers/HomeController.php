<?php

namespace App\Http\Controllers;

use App\Services\ApiClient;
use Illuminate\Support\Facades\Session;

class HomeController extends Controller
{
    private ApiClient $apiClient;

    public function __construct(ApiClient $apiClient)
    {
        $this->apiClient = $apiClient;
    }

    /**
     * Display landing page
     */
    public function index()
    {
        $activityTabs = $this->activityTabs();
        $activitySlug = request('activity_slug', 'city-tour');
        if (!isset($activityTabs[$activitySlug])) {
            $activitySlug = 'city-tour';
        }

        $activityRecommendationHomeEnabled = (bool) config('api.flags.activity_recommendation_home_enabled', true);
        $activityRecommendationEndpointEnabled = (bool) config('api.flags.activity_recommendation_endpoint_enabled', true);
        $activityRecommendationFeatureEnabled = $activityRecommendationHomeEnabled && $activityRecommendationEndpointEnabled;

        $landing = $this->apiClient->get('public/landing');
        $landingData = $landing['data'] ?? [];
        $landingFailed = ($landing['success'] ?? true) === false;

        $recommendationData = [];
        $activityRecommendationError = null;

        if ($activityRecommendationFeatureEnabled) {
            $recommendations = $this->apiClient->get(
                "public/activities/{$activitySlug}/recommendations",
                ['page' => 1, 'limit' => 3],
            );
            $recommendationData = $recommendations['data'] ?? [];
            $recommendationFailed = ($recommendations['success'] ?? true) === false;
            $recommendationErrorInfo = $recommendationData['error_info'] ?? null;

            if ($recommendationFailed) {
                $activityRecommendationError = [
                    'code' => 'API_CLIENT_ERROR',
                    'message' => $recommendations['error'] ?? 'Không thể tải gợi ý hoạt động.',
                ];
            } elseif (is_array($recommendationErrorInfo) && !empty($recommendationErrorInfo)) {
                $activityRecommendationError = [
                    'code' => $recommendationErrorInfo['endpoint_error_code'] ?? 'ACTIVITY_RECOMMENDATION_ENDPOINT_ERROR',
                    'message' => $recommendationErrorInfo['endpoint_error_message'] ?? 'Không thể tải gợi ý hoạt động.',
                ];
            }
        }

        $selectedActivity = $activityTabs[$activitySlug];

        $destinations = $this->attachFavoriteState($landingData['highlights'] ?? []);

        return view('pages.public.home', [
            'destinations' => $destinations,
            'categories' => $landingData['categories'] ?? [],
            'homeError' => $landingFailed ? ($landing['error'] ?? 'Không thể tải dữ liệu trang chủ.') : null,
            'activityTabs' => $activityTabs,
            'selectedActivitySlug' => $activitySlug,
            'selectedActivityName' => $selectedActivity['name'],
            'selectedActivityDescription' => $selectedActivity['description'],
            'activityRecommendationHomeEnabled' => $activityRecommendationHomeEnabled,
            'activityRecommendationEndpointEnabled' => $activityRecommendationEndpointEnabled,
            'activityRecommendationFeatureEnabled' => $activityRecommendationFeatureEnabled,
            'activityRecommendations' => [
                'activity' => $recommendationData['activity'] ?? $selectedActivity,
                'highlight_destinations' => $recommendationData['highlight_destinations'] ?? [],
                'recommended_destinations' => $recommendationData['recommended_destinations'] ?? [],
                'trending' => $recommendationData['trending'] ?? [],
            ],
            'activityRecommendationError' => $activityRecommendationError,
        ]);
    }

    /**
     * Default activity tabs for the home page.
     *
     * @return array<string, array<string, string>>
     */
    private function activityTabs(): array
    {
        return [
            'city-tour' => [
                'name' => 'City tour',
                'description' => 'Khám phá các điểm nổi bật khu trung tâm và đô thị.',
            ],
            'food-tour' => [
                'name' => 'Food tour',
                'description' => 'Thưởng thức ẩm thực địa phương và street food.',
            ],
            'chill-bien' => [
                'name' => 'Chill biển',
                'description' => 'Nghỉ dưỡng, thư giãn ở bờ biển và quán cà phê view biển.',
            ],
            'kham-pha-thien-nhien' => [
                'name' => 'Khám phá thiên nhiên',
                'description' => 'Trải nghiệm núi, rừng, thác và các hoạt động ngoài trời.',
            ],
            'van-hoa-lich-su' => [
                'name' => 'Văn hóa lịch sử',
                'description' => 'Tham quan di tích, bảo tàng và các điểm đến văn hóa.',
            ],
        ];
    }

    /**
     * Attach is_favorite flag from current user's favorites.
     *
     * @param array<int, array<string, mixed>> $destinations
     * @return array<int, array<string, mixed>>
     */
    private function attachFavoriteState(array $destinations): array
    {
        if ($destinations === [] || !Session::has('access_token')) {
            return $destinations;
        }

        $favoriteResponse = $this->apiClient->get('me/favorites', ['page' => 1, 'limit' => 100]);
        $favoriteItems = $favoriteResponse['data'] ?? [];

        $favoriteIdMap = collect($favoriteItems)
            ->pluck('id')
            ->filter(fn ($id) => $id !== null)
            ->map(fn ($id) => (int) $id)
            ->flip();

        return collect($destinations)
            ->map(function ($destination) use ($favoriteIdMap) {
                if (!is_array($destination)) {
                    return $destination;
                }

                $destinationId = (int) ($destination['id'] ?? 0);
                $destination['is_favorite'] = $favoriteIdMap->has($destinationId);
                return $destination;
            })
            ->all();
    }
}
