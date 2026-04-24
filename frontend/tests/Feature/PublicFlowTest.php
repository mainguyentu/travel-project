<?php

namespace Tests\Feature;

use App\Services\ApiClient;
use Illuminate\Support\Facades\Config;
use Mockery\MockInterface;
use Tests\TestCase;

class PublicFlowTest extends TestCase
{
    // public function test_home_page_renders_with_landing_data(): void
    // {
    //     $this->mock(ApiClient::class, function (MockInterface $mock): void {
    //         $mock->shouldReceive('get')
    //             ->once()
    //             ->with('public/landing')
    //             ->andReturn([
    //                 'success' => true,
    //                 'data' => [
    //                     'highlights' => [['id' => 1, 'name' => 'My Khe']],
    //                     'categories' => [['id' => 10, 'name' => 'Beach', 'slug' => 'beach']],
    //                 ],
    //             ]);

    //         $mock->shouldReceive('get')
    //             ->once()
    //             ->with('public/activities/city-tour/recommendations', ['page' => 1, 'limit' => 3])
    //             ->andReturn([
    //                 'success' => true,
    //                 'data' => [
    //                     'activity' => ['id' => 1, 'slug' => 'city-tour', 'name' => 'City tour', 'description' => 'Khám phá các điểm nổi bật khu trung tâm và đô thị.'],
    //                     'highlight_destinations' => [['id' => 11, 'name' => 'Dragon Bridge', 'rating_avg' => 4.8]],
    //                     'recommended_destinations' => [['id' => 12, 'name' => 'Han River', 'rating_avg' => 4.6]],
    //                     'trending' => [['id' => 13, 'name' => 'Sun Wheel', 'rating_avg' => 4.5]],
    //                     'error_info' => null,
    //                 ],
    //             ]);
    //     });

    //     $response = $this->get('/');

    //     $response->assertOk();
    //     $response->assertViewIs('pages.public.home');
    //     $response->assertViewHas('featured', fn (array $featured) => count($featured) === 1);
    //     $response->assertViewHas('categories', fn (array $categories) => count($categories) === 1);
    //     $response->assertViewHas('selectedActivitySlug', fn (string $slug) => $slug === 'city-tour');
    //     $response->assertSee('Dragon Bridge');
    //     $response->assertSee('Han River');
    //     $response->assertSee('Sun Wheel');
    // }

    // public function test_home_page_shows_activity_api_error_banner_when_recommendations_fail(): void
    // {
    //     $this->mock(ApiClient::class, function (MockInterface $mock): void {
    //         $mock->shouldReceive('get')
    //             ->once()
    //             ->with('public/landing')
    //             ->andReturn([
    //                 'success' => true,
    //                 'data' => [
    //                     'highlights' => [],
    //                     'categories' => [],
    //                 ],
    //             ]);

    //         $mock->shouldReceive('get')
    //             ->once()
    //             ->with('public/activities/city-tour/recommendations', ['page' => 1, 'limit' => 3])
    //             ->andReturn([
    //                 'success' => true,
    //                 'data' => [
    //                     'activity' => ['id' => 1, 'slug' => 'city-tour', 'name' => 'City tour'],
    //                     'highlight_destinations' => [],
    //                     'recommended_destinations' => [],
    //                     'trending' => [],
    //                     'error_info' => [
    //                         'endpoint_error_code' => 'ACTIVITY_RECOMMENDATION_ENDPOINT_ERROR',
    //                         'endpoint_error_message' => 'Failed to compute recommendations',
    //                     ],
    //                 ],
    //             ]);
    //     });

    //     $response = $this->get('/');

    //     $response->assertOk();
    //     $response->assertSee('Lỗi API Endpoint ACTIVITY_RECOMMENDATION_ENDPOINT_ERROR');
    // }

    // public function test_home_page_shows_rollout_info_and_skips_recommendation_api_when_feature_disabled(): void
    // {
    //     Config::set('api.flags.activity_recommendation_home_enabled', false);
    //     Config::set('api.flags.activity_recommendation_endpoint_enabled', true);

    //     $this->mock(ApiClient::class, function (MockInterface $mock): void {
    //         $mock->shouldReceive('get')
    //             ->once()
    //             ->with('public/landing')
    //             ->andReturn([
    //                 'success' => true,
    //                 'data' => [
    //                     'highlights' => [],
    //                     'categories' => [],
    //                 ],
    //             ]);
    //     });

    //     $response = $this->get('/');

    //     $response->assertOk();
    //     $response->assertSee('Tính năng gợi ý hoạt động đang được triển khai.');
    //     $response->assertSee('Endpoint: ON');
    //     $response->assertSee('Home integration: OFF');
    // }

    public function test_destinations_index_applies_query_filters_and_pagination_meta(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('get')
                ->once()
                ->withArgs(function (string $path, array $query): bool {
                    return $path === 'destinations'
                        && ($query['page'] ?? null) === '2'
                        && ($query['category_slug'] ?? null) === 'beach'
                        && ($query['price_level'] ?? null) === 'free'
                        && ($query['rating_min'] ?? null) === '4'
                        && ($query['keyword'] ?? null) === 'sunny'
                        && ($query['sort'] ?? null) === 'views';
                })
                ->andReturn([
                    'success' => true,
                    'data' => [['id' => 1, 'name' => 'Sunny Beach']],
                    'meta' => ['page' => 2, 'limit' => 20, 'total' => 45],
                ]);

            $mock->shouldReceive('get')
                ->once()
                ->with('public/landing')
                ->andReturn([
                    'success' => true,
                    'data' => ['categories' => [['id' => 10, 'name' => 'Beach', 'slug' => 'beach']]],
                ]);
        });

        $response = $this->get('/destinations?page=2&category=beach&price_level=free&rating=4&keyword=sunny&sort=views');

        $response->assertOk();
        $response->assertViewIs('pages.public.destinations.index');
        $response->assertViewHas('destinations', fn (array $destinations) => count($destinations) === 1);
        $response->assertViewHas('pagination', function (array $pagination): bool {
            return ($pagination['current_page'] ?? null) === 2
                && ($pagination['last_page'] ?? null) === 3
                && ($pagination['total'] ?? null) === 45;
        });
    }

    public function test_destination_detail_route_is_not_available(): void
    {
        $response = $this->get('/destinations/999');

        $response->assertNotFound();
    }
}
