<?php

namespace Tests\Feature;

use App\Services\ApiClient;
use Mockery\MockInterface;
use Tests\TestCase;

class AuthFlowTest extends TestCase
{
    public function test_login_success_redirects_to_profile_and_stores_session(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('post')
                ->once()
                ->with('auth/login', ['email' => 'user@alats.vn', 'password' => 'User@123'])
                ->andReturn([
                    'success' => true,
                    'data' => [
                        'access_token' => 'access-token',
                        'refresh_token' => 'refresh-token',
                    ],
                ]);

            $mock->shouldReceive('get')
                ->once()
                ->with('admin/stats/top-views')
                ->andReturn(['success' => false, 'error' => 'forbidden']);
        });

        $response = $this->post('/login', [
            'email' => 'user@alats.vn',
            'password' => 'User@123',
        ]);

        $response->assertRedirect('/profile');
        $this->assertSame('access-token', session('access_token'));
        $this->assertSame('refresh-token', session('refresh_token'));
        $this->assertSame('user', session('user.role'));
    }

    public function test_login_failure_returns_validation_error_message(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('post')
                ->once()
                ->with('auth/login', ['email' => 'wrong@alats.vn', 'password' => 'bad-pass'])
                ->andReturn(['success' => false, 'error' => 'Invalid credentials']);
        });

        $response = $this->from('/login')->post('/login', [
            'email' => 'wrong@alats.vn',
            'password' => 'bad-pass',
        ]);

        $response->assertRedirect('/login');
        $response->assertSessionHasErrors(['email', 'api']);
        $this->assertNull(session('access_token'));
    }

    public function test_register_success_redirects_to_login_with_success_message(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('post')
                ->once()
                ->with('auth/register', [
                    'name' => 'New User',
                    'email' => 'new@alats.vn',
                    'password' => 'User@12345',
                ])
                ->andReturn(['success' => true, 'data' => ['id' => 1]]);
        });

        $response = $this->post('/register', [
            'name' => 'New User',
            'email' => 'new@alats.vn',
            'password' => 'User@12345',
            'password_confirmation' => 'User@12345',
        ]);

        $response->assertRedirect('/login');
        $response->assertSessionHas('success');
    }

    public function test_register_failure_returns_api_error(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('post')
                ->once()
                ->andReturn(['success' => false, 'error' => 'Email already exists']);
        });

        $response = $this->from('/register')->post('/register', [
            'name' => 'Dup User',
            'email' => 'dup@alats.vn',
            'password' => 'User@12345',
            'password_confirmation' => 'User@12345',
        ]);

        $response->assertRedirect('/register');
        $response->assertSessionHasErrors(['api']);
    }

    public function test_logout_clears_session_and_redirects_home(): void
    {
        $this->mock(ApiClient::class, function (MockInterface $mock): void {
            $mock->shouldReceive('post')
                ->once()
                ->with('auth/logout', ['refresh_token' => 'refresh-token'])
                ->andReturn(['success' => true]);
        });

        $response = $this->withSession([
            'access_token' => 'access-token',
            'refresh_token' => 'refresh-token',
            'user' => ['email' => 'user@alats.vn', 'role' => 'user'],
        ])->post('/logout');

        $response->assertRedirect('/');
        $this->assertNull(session('access_token'));
        $this->assertNull(session('refresh_token'));
        $this->assertNull(session('user'));
    }
}
