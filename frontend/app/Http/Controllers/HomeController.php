<?php

namespace App\Http\Controllers;

use App\Services\ApiClient;

class HomeController extends Controller
{
    private ApiClient $apiClient;

    public function __construct(ApiClient $apiClient)
    {
        $this->apiClient = $apiClient;
    }

    /**
     * Display landing page
     */
    public function index()
    {
        $landing = $this->apiClient->get('public/landing');
        $landingData = $landing['data'] ?? [];
        $landingFailed = ($landing['success'] ?? true) === false;

        return view('pages.public.home', [
            'featured' => $landingData['highlights'] ?? [],
            'categories' => $landingData['categories'] ?? [],
            'homeError' => $landingFailed ? ($landing['error'] ?? 'Không thể tải dữ liệu trang chủ.') : null,
        ]);
    }
}
