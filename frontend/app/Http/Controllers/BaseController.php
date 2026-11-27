<?php

namespace App\Http\Controllers;

use App\Services\ApiClient;
use Illuminate\Http\Request;

abstract class BaseController
{
    protected function api(?Request $request = null): ApiClient
    {
        $client = new ApiClient(session('access_token'), session('refresh_token'));
        $client->onTokensRefreshed(function ($access, $refresh) {
            session(['access_token' => $access, 'refresh_token' => $refresh]);
        });
        $client->onUnauthenticated(function () {
            session()->forget(['access_token', 'refresh_token', 'user', 'is_admin']);
        });

        return $client;
    }

    protected function apiError(array $body, string $fallback = 'Có lỗi xảy ra.'): string
    {
        return $body['error']['message'] ?? $fallback;
    }
}
