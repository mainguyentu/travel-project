<?php

namespace Tests\Feature;

use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class JourneysTest extends TestCase
{
    public function test_login_success_sets_session_and_role_probe(): void
    {
        Http::fake([
            '*/auth/login' => Http::response([
                'success' => true,
                'data' => ['access_token' => 'a', 'refresh_token' => 'r', 'token_type' => 'Bearer', 'expires_in' => 30],
            ], 200),
            '*/admin/stats/top-views' => Http::response(['success' => true, 'data' => []], 200),
        ]);

        $response = $this->post('/login', ['email' => 'admin@alats.vn', 'password' => 'secret']);
        $response->assertRedirect('/admin');
        $this->assertEquals('a', session('access_token'));
        $this->assertTrue(session('is_admin'));
    }

    public function test_login_failure_preserves_email(): void
    {
        Http::fake([
            '*/auth/login' => Http::response([
                'success' => false,
                'error' => ['code' => 'UNAUTHORIZED', 'message' => 'Invalid email or password', 'details' => []],
                'meta' => [],
            ], 401),
        ]);

        $response = $this->post('/login', ['email' => 'u@x.vn', 'password' => 'wrong']);
        $response->assertRedirect();
        $response->assertSessionHas('error');
    }

    public function test_favorites_roundtrip_through_me_api(): void
    {
        Http::fake([
            '*/me/favorites/7' => Http::response(['success' => true, 'data' => []], 200),
            '*/me/favorites*' => Http::response([
                'success' => true,
                'data' => [['id' => 7, 'name' => 'Island', 'slug' => 'island']],
                'meta' => ['page' => 1, 'limit' => 20],
            ], 200),
        ]);

        $session = ['access_token' => 'a', 'refresh_token' => 'r'];
        $this->withSession($session)->post('/favorites/7')->assertRedirect();
        $this->withSession($session)->get('/my-favorites')->assertOk()->assertSee('Island');
        $this->withSession($session)->delete('/favorites/7')->assertRedirect();
    }

    public function test_rating_validation_blocks_out_of_range(): void
    {
        $this->withSession(['access_token' => 'a'])
            ->put('/ratings/2', ['rating_score' => 9])
            ->assertSessionHasErrors('rating_score');
    }

    public function test_admin_users_page_renders(): void
    {
        Http::fake([
            '*/admin/users*' => Http::response([
                'success' => true,
                'data' => [['id' => 1, 'name' => 'A', 'email' => 'a@x.vn', 'role' => 'user', 'status' => 'active']],
                'meta' => ['page' => 1, 'limit' => 20, 'total' => 1],
            ], 200),
        ]);

        $this->withSession(['access_token' => 'a', 'is_admin' => true])
            ->get('/admin/users')->assertOk()->assertSee('a@x.vn');
    }

    public function test_admin_stats_page_renders_without_500(): void
    {
        Http::fake([
            '*/admin/stats/*' => Http::response(['success' => true, 'data' => []], 200),
        ]);

        $this->withSession(['access_token' => 'a', 'is_admin' => true])
            ->get('/admin/stats')->assertOk()->assertSee('Thống kê tổng hợp');
    }

    public function test_admin_dashboard_and_tables_use_ocean_theme(): void
    {
        Http::fake([
            '*/admin/stats/*' => Http::response(['success' => true, 'data' => [
                ['id' => 1, 'name' => 'Biển', 'slug' => 'bien', 'rating_avg' => 4.5, 'view_count' => 10, 'price_level' => 'low', 'status' => 'active'],
            ]], 200),
            '*/admin/users*' => Http::response(['success' => true,
                'data' => [['id' => 1, 'name' => 'A', 'email' => 'a@x.vn', 'role' => 'admin', 'status' => 'active']],
                'meta' => ['page' => 1, 'limit' => 20, 'total' => 1]], 200),
            '*/admin/destinations*' => Http::response(['success' => true,
                'data' => [['id' => 1, 'name' => 'Biển', 'slug' => 'bien', 'price_level' => 'low', 'status' => 'active', 'rating_avg' => 4.5, 'view_count' => 10]],
                'meta' => ['page' => 1, 'limit' => 20, 'total' => 1]], 200),
            '*/admin/categories*' => Http::response(['success' => true,
                'data' => [['id' => 1, 'name' => 'Biển', 'slug' => 'bien']]], 200),
            '*/admin/audit-logs*' => Http::response(['success' => true,
                'data' => [['id' => 1, 'actor_user_id' => 1, 'action' => 'create',
                    'entity' => 'destination', 'entity_id' => '1', 'detail' => [], 'created_at' => '2026-11-27T00:00:00Z']],
                'meta' => ['page' => 1, 'limit' => 20, 'total' => 1]], 200),
        ]);

        $admin = ['access_token' => 'a', 'is_admin' => true];
        $this->withSession($admin)->get('/admin')->assertOk()
            ->assertSee('kpi', false)->assertSee('admin-table', false);
        $this->withSession($admin)->get('/admin/users')->assertOk()->assertSee('badge-admin', false);
        $this->withSession($admin)->get('/admin/destinations')->assertOk()->assertSee('toolbar', false);
        $this->withSession($admin)->get('/admin/audit-logs')->assertOk()->assertSee('badge-ok', false);
        $this->withSession($admin)->get('/admin/stats')->assertOk()->assertSee('panels', false);
    }

    public function test_admin_bulk_audit_and_activity_pages(): void
    {
        Http::fake([
            '*/admin/destinations/bulk' => Http::response([
                'success' => true, 'data' => [['id' => 9, 'name' => 'Bulk', 'slug' => 'bulk-9']],
            ], 201),
            '*/admin/audit-logs*' => Http::response([
                'success' => true,
                'data' => [['id' => 1, 'actor_user_id' => 1, 'action' => 'bulk_create',
                    'entity' => 'destination', 'entity_id' => null,
                    'detail' => ['count' => 1], 'created_at' => '2026-11-27T00:00:00Z']],
                'meta' => ['page' => 1, 'limit' => 20, 'total' => 1],
            ], 200),
            '*/public/activities/bien/recommendations*' => Http::response([
                'success' => true,
                'data' => ['activity' => ['name' => 'Biển', 'slug' => 'bien'],
                    'recommended_destinations' => [['id' => 1, 'name' => 'Mỹ Khê', 'slug' => 'my-khe']],
                    'trending' => []],
            ], 200),
        ]);

        $admin = ['access_token' => 'a', 'is_admin' => true];
        $this->withSession($admin)
            ->post('/admin/destinations/bulk', ['payload' => '[{"name":"Bulk","slug":"bulk-9"}]'])
            ->assertRedirect();
        $this->withSession($admin)
            ->get('/admin/audit-logs')->assertOk()->assertSee('bulk_create');
        $this->get('/activities/bien')->assertOk()->assertSee('Mỹ Khê');
    }
}
