<?php

return [
    // API Base URL - Backend API Gateway
    'base_url' => env('API_BASE_URL', 'http://localhost:8080'),
    
    // API Version
    'version' => env('API_VERSION', 'v1'),
    
    // Full API endpoint
    'endpoint' => env('API_BASE_URL', 'http://localhost:8080') . '/api/' . env('API_VERSION', 'v1'),
    
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
];
