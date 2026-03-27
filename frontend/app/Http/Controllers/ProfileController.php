<?php

namespace App\Http\Controllers;

use App\Http\Requests\RateDestinationRequest;
use App\Services\ApiClient;
use Illuminate\Support\Facades\Session;

class ProfileController extends Controller
{
    private ApiClient $apiClient;

    public function __construct(ApiClient $apiClient)
    {
        $this->apiClient = $apiClient;
    }

    /**
     * Display user profile
     */
    public function index()
    {
        $user = Session::get('user');

        return view('pages.public.profile', [
            'user' => $user,
        ]);
    }

    /**
     * Display user favorites
     */
    public function favorites()
    {
        $response = $this->apiClient->get('me/favorites');

        return view('pages.public.favorites', [
            'favorites' => $response['data'] ?? [],
        ]);
    }

    /**
     * Add favorite
     */
    public function addFavorite($destinationId)
    {
        $response = $this->apiClient->post("me/favorites/{$destinationId}");

        if (request()->wantsJson()) {
            return response()->json($response);
        }

        return back()->with('success', 'Đã thêm vào yêu thích');
    }

    /**
     * Remove favorite
     */
    public function removeFavorite($destinationId)
    {
        $response = $this->apiClient->delete("me/favorites/{$destinationId}");

        if (request()->wantsJson()) {
            return response()->json($response);
        }

        return back()->with('success', 'Đã xoá khỏi yêu thích');
    }

    /**
     * Rate destination
     */
    public function rate(RateDestinationRequest $request, $destinationId)
    {
        $validated = $request->validated();

        $payload = [
            'rating_score' => $validated['rating_score'],
            'comment' => $validated['comment'] ?? null,
        ];

        $response = $this->apiClient->put("me/ratings/{$destinationId}", $payload);

        if (request()->wantsJson()) {
            return response()->json($response);
        }

        return back()->with('success', 'Cảm ơn đã đánh giá !');
    }
}
