<?php

namespace Tests\Feature;

use App\Models\User;
use App\Services\ApiClient;
use Mockery\MockInterface;
use Tests\TestCase;

class AdminFlowTest extends TestCase
{
    private function adminUser(): User
    {
        return User::factory()->make([
            'name' => 'Admin User',
            'email' => 'admin@alats.vn',
        ]);
    }

    private function adminSession(): array
    {
        return [
            'access_token' => 'admin-token',
            'user' => ['email' => 'admin@alats.vn', 'role' => 'admin'],
        ];
    }

    public function test_admin_dashboard_renders_stats(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('get')
                ->times(5)
                ->andReturn(
                    ['success' => true, 'meta' => ['total' => 10]],
                    ['success' => true, 'meta' => ['total' => 25]],
                    ['success' => true, 'data' => [['id' => 1, 'name' => 'A', 'favorite_count' => 7]]],
                    ['success' => true, 'data' => [['id' => 2, 'name' => 'B', 'rating_avg' => 4.5]]],
                    ['success' => true, 'data' => [['id' => 3, 'name' => 'C', 'view_count' => 123]]],
                );
        });

        $response = $this->actingAs($this->adminUser())
            ->withSession($this->adminSession())
            ->get('/admin');

        $response->assertOk();
        $response->assertViewIs('pages.admin.dashboard');
        $response->assertViewHas('stats', fn (array $stats) => ($stats['total_users'] ?? 0) === 10 && ($stats['total_destinations'] ?? 0) === 25);
    }

    public function test_admin_users_page_renders_with_data(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('get')
                ->once()
                ->with('admin/users', ['page' => 1, 'limit' => 50])
                ->andReturn([
                    'success' => true,
                    'data' => [[
                        'id' => 1,
                        'name' => 'Normal User',
                        'email' => 'user@alats.vn',
                        'role' => 'user',
                        'status' => 'active',
                    ]],
                ]);
        });

        $response = $this->actingAs($this->adminUser())
            ->withSession($this->adminSession())
            ->get('/admin/users');

        $response->assertOk();
        $response->assertViewIs('pages.admin.users.index');
        $response->assertViewHas('users', fn (array $users) => count($users) === 1);
    }

    public function test_admin_categories_page_shows_error_state_when_api_fails(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('get')
                ->once()
                ->with('admin/categories')
                ->andReturn([
                    'success' => false,
                    'error' => 'backend unavailable',
                    'data' => [],
                ]);
        });

        $response = $this->actingAs($this->adminUser())
            ->withSession($this->adminSession())
            ->get('/admin/categories');

        $response->assertOk();
        $response->assertViewIs('pages.admin.categories.index');
        $response->assertViewHas('categoriesError', 'backend unavailable');
    }

    public function test_admin_destinations_page_renders_with_data(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('get')
                ->once()
                ->with('admin/destinations', ['page' => 1, 'limit' => 50])
                ->andReturn([
                    'success' => true,
                    'data' => [[
                        'id' => 1,
                        'name' => 'My Khe',
                        'slug' => 'my-khe',
                        'categories' => [['id' => 10, 'name' => 'Beach', 'slug' => 'beach']],
                        'rating_avg' => 4.8,
                        'view_count' => 99,
                    ]],
                ]);
        });

        $response = $this->actingAs($this->adminUser())
            ->withSession($this->adminSession())
            ->get('/admin/destinations');

        $response->assertOk();
        $response->assertViewIs('pages.admin.destinations.index');
        $response->assertViewHas('destinations', fn (array $destinations) => count($destinations) === 1);
    }

    public function test_admin_stats_page_renders_metrics_lists(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('get')
                ->times(3)
                ->andReturn(
                    ['success' => true, 'data' => [['id' => 1]]],
                    ['success' => true, 'data' => [['id' => 2]]],
                    ['success' => true, 'data' => [['id' => 3]]],
                );
        });

        $response = $this->actingAs($this->adminUser())
            ->withSession($this->adminSession())
            ->get('/admin/stats');

        $response->assertOk();
        $response->assertViewIs('pages.admin.stats');
        $response->assertViewHas('stats', function (array $stats): bool {
            return count($stats['top_favorites'] ?? []) === 1
                && count($stats['top_ratings'] ?? []) === 1
                && count($stats['top_views'] ?? []) === 1;
        });
    }
}
