<?php

namespace Tests\Feature;

use App\Models\User;
use App\Services\ApiClient;
use Mockery\MockInterface;
use Tests\TestCase;

class MiddlewareAccessTest extends TestCase
{
    public function test_profile_route_redirects_guest_to_login(): void
    {
        $this->get('/profile')->assertRedirect('/login');
    }

    public function test_profile_route_allows_authenticated_session(): void
    {
        $response = $this->withSession([
            'access_token' => 'token',
            'user' => ['email' => 'user@alats.vn', 'role' => 'user'],
        ])->get('/profile');

        $response->assertOk();
        $response->assertViewIs('pages.public.profile');
    }

    public function test_admin_route_forbidden_for_non_admin_user(): void
    {
        $response = $this->withSession([
            'access_token' => 'token',
            'user' => ['email' => 'user@alats.vn', 'role' => 'user'],
        ])->get('/admin');

        $response->assertForbidden();
    }

    public function test_admin_dashboard_loads_for_admin_user(): void
    {
        $user = User::factory()->make([
            'name' => 'Admin Test',
            'email' => 'admin@alats.vn',
        ]);

        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('get')
                ->times(5)
                ->andReturn(
                    ['success' => true, 'meta' => ['total' => 12]],
                    ['success' => true, 'meta' => ['total' => 34]],
                    ['success' => true, 'data' => []],
                    ['success' => true, 'data' => []],
                    ['success' => true, 'data' => []],
                );
        });

            $response = $this->actingAs($user)->withSession([
            'access_token' => 'token',
            'user' => ['email' => 'admin@alats.vn', 'role' => 'admin'],
        ])->get('/admin');

        $response->assertOk();
        $response->assertViewIs('pages.admin.dashboard');
        $response->assertViewHas('stats', fn (array $stats) => ($stats['total_users'] ?? 0) === 12 && ($stats['total_destinations'] ?? 0) === 34);
    }
}
