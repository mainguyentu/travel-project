<?php

return [
    // API Base URL - Backend API Gateway
    'base_url' => env('API_BASE_URL', 'http://localhost:8080'),

    // API URL used by browser-side JavaScript
    'browser_base_url' => env('API_BROWSER_BASE_URL', env('API_BASE_URL', 'http://localhost:8080')),
    
    // API Version
    'version' => env('API_VERSION', 'v1'),
    
    // Full API endpoint
    'endpoint' => env('API_BASE_URL', 'http://localhost:8080') . '/api/' . env('API_VERSION', 'v1'),

    // Full API endpoint used by browser-side JavaScript
    'browser_endpoint' => env('API_BROWSER_BASE_URL', env('API_BASE_URL', 'http://localhost:8080')) . '/api/' . env('API_VERSION', 'v1'),
    
    // Request timeout (seconds)
    'timeout' => env('API_TIMEOUT', 30),
    
    // Retry configuration
    'retry' => [
        'enabled' => true,
        'max_attempts' => 3,
        'delay' => 1000, // milliseconds
    ],
    
    // CORS and SSL verification
    'verify_ssl' => env('API_VERIFY_SSL', true),

    // Feature flags for staged rollout
    'flags' => [
        'activity_recommendation_endpoint_enabled' => env('FEATURE_ACTIVITY_RECOMMENDATION_ENDPOINT_ENABLED', true),
        'activity_recommendation_home_enabled' => env('FEATURE_ACTIVITY_RECOMMENDATION_HOME_ENABLED', true),
    ],

    // Frontend response cache (Redis)
    'cache' => [
        'enabled' => env('API_CACHE_ENABLED', true),
        'store' => env('API_CACHE_STORE', env('CACHE_STORE', 'redis')),
        'default_ttl' => env('API_CACHE_TTL', 120),
        'path_ttl' => [
            'public/landing' => env('API_CACHE_TTL_LANDING', 300),
            'destinations' => env('API_CACHE_TTL_DESTINATIONS', 180),
            'admin/stats' => env('API_CACHE_TTL_ADMIN_STATS', 60),
        ],
        'public_path_prefixes' => [
            'public/',
            'destinations',
        ],
        'cache_authenticated' => env('API_CACHE_AUTHENTICATED', false),
        'authenticated_path_prefixes' => [
            'admin/stats',
        ],
        'invalidate_on_write' => env('API_CACHE_INVALIDATE_ON_WRITE', true),
        'key_prefix' => env('API_CACHE_PREFIX', 'frontend:api-response'),
        'registry_key' => env('API_CACHE_REGISTRY_KEY', 'frontend:api-response:keys'),
    ],
];
