<?php

namespace Tests\Feature;

use Illuminate\Support\Facades\Http;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * A basic test example.
     */
    public function test_the_application_returns_a_successful_response(): void
    {
        Http::fake([
            '*/public/landing' => Http::response([
                'success' => true,
                'data' => ['highlights' => [], 'categories' => [], 'top_ratings' => [], 'top_favorites' => []],
                'meta' => [],
            ], 200),
        ]);

        $response = $this->get('/');

        $response->assertStatus(200);
    }
}
