<?php

namespace App\Http\Controllers;

use App\Services\ApiClient;

class DestinationController extends Controller
{
    private ApiClient $apiClient;

    public function __construct(ApiClient $apiClient)
    {
        $this->apiClient = $apiClient;
    }

    /**
     * Display destination list
     */
    public function index()
    {
        $page = request('page', 1);
        $category = request('category_slug', request('category'));
        $priceLevel = request('price_level');
        $rating = request('rating_min', request('rating'));
        $keyword = request('keyword', request('search'));
        $sort = request('sort');

        $query = ['page' => $page, 'limit' => 15];
        
        if ($category) {
            $query['category_slug'] = $category;
        }
        if ($priceLevel) {
            $query['price_level'] = $priceLevel;
        }
        if ($rating) {
            $query['rating_min'] = $rating;
        }
        if ($keyword) {
            $query['keyword'] = $keyword;
        }
        if ($sort) {
            $query['sort'] = $sort;
        }

        $response = $this->apiClient->get('destinations', $query);
        $requestFailed = ($response['success'] ?? true) === false;
        $meta = $response['meta'] ?? [];
        $pageValue = (int) ($meta['page'] ?? 1);
        $limitValue = (int) ($meta['limit'] ?? 15);
        $total = (int) ($meta['total'] ?? 0);
        $lastPage = $limitValue > 0 ? (int) ceil($total / $limitValue) : 1;

        $landing = $this->apiClient->get('public/landing');
        $landingData = $landing['data'] ?? [];

        return view('pages.public.destinations.index', [
            'destinations' => $response['data'] ?? [],
            'pagination' => [
                'current_page' => $pageValue,
                'last_page' => max($lastPage, 1),
                'limit' => $limitValue,
                'total' => $total,
            ],
            'categories' => $landingData['categories'] ?? [],
            'listError' => $requestFailed ? ($response['error'] ?? 'Không thể tải danh sách điểm đến.') : null,
        ]);
    }

}
