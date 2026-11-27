<?php

namespace Tests\Feature;

use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class GuardsTest extends TestCase
{
    public function test_guest_can_view_public_pages(): void
    {
        Http::fake([
            '*/public/landing' => Http::response([
                'success' => true,
                'data' => ['highlights' => [], 'categories' => [], 'top_ratings' => [], 'top_favorites' => []],
                'meta' => [],
            ], 200),
            '*/destinations*' => Http::response([
                'success' => true, 'data' => [], 'meta' => ['page' => 1, 'limit' => 15, 'total' => 0],
            ], 200),
        ]);

        $this->get('/')->assertOk();
        $this->get('/destinations')->assertOk();
        $this->get('/login')->assertOk();
        $this->get('/register')->assertOk();
    }

    public function test_auth_pages_require_login(): void
    {
        $this->get('/profile')->assertRedirect('/login');
        $this->get('/my-favorites')->assertRedirect('/login');
        $this->post('/favorites/1')->assertRedirect('/login');
        $this->put('/ratings/1', ['rating_score' => 5])->assertRedirect('/login');
    }

    public function test_admin_pages_require_admin(): void
    {
        // Chưa login -> về login.
        $this->get('/admin')->assertRedirect('/login');

        // Login user thường -> 403.
        $this->withSession(['access_token' => 'x', 'is_admin' => false])
            ->get('/admin')->assertForbidden();
        $this->withSession(['access_token' => 'x', 'is_admin' => false])
            ->get('/admin/users')->assertForbidden();
    }

    public function test_guest_middleware_redirects_logged_in(): void
    {
        $this->withSession(['access_token' => 'x'])
            ->get('/login')->assertRedirect('/');
    }
}
