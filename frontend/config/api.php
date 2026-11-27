<?php

return [
    'base_url' => env('API_BASE_URL', 'http://127.0.0.1:8001/api/v1'),

    'cache' => [
        'enabled' => env('API_CACHE_ENABLED', true),
        'ttl' => [
            'public' => (int) env('API_CACHE_TTL_PUBLIC', 300),
            'destinations' => (int) env('API_CACHE_TTL_DESTINATIONS', 120),
            'default' => (int) env('API_CACHE_TTL_DEFAULT', 60),
        ],
    ],
];
