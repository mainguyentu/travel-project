<?php

namespace Tests\Feature;

use App\Services\ApiClient;
use Mockery\MockInterface;
use Tests\TestCase;

class PublicFlowTest extends TestCase
{
    public function test_home_page_renders_with_landing_data(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('get')
                ->once()
                ->with('public/landing')
                ->andReturn([
                    'success' => true,
                    'data' => [
                        'highlights' => [['id' => 1, 'name' => 'My Khe']],
                        'categories' => [['id' => 10, 'name' => 'Beach', 'slug' => 'beach']],
                    ],
                ]);
        });

        $response = $this->get('/');

        $response->assertOk();
        $response->assertViewIs('pages.public.home');
        $response->assertViewHas('featured', fn (array $featured) => count($featured) === 1);
        $response->assertViewHas('categories', fn (array $categories) => count($categories) === 1);
    }

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

    public function test_destination_detail_404_when_api_returns_failure(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('get')
                ->once()
                ->with('destinations/999')
                ->andReturn([
                    'success' => false,
                    'error' => 'Not found',
                ]);
        });

        $response = $this->get('/destinations/999');

        $response->assertNotFound();
    }
}
