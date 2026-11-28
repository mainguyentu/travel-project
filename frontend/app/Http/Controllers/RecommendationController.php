<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class RecommendationController extends BaseController
{
    public function index(Request $request)
    {
        $limit = min(20, max(1, (int) $request->input('limit', 10)));
        $rec = $this->api()->get('me/recommendations', ['limit' => $limit]);
        $planDays = min(10, max(1, (int) $request->input('days', 5)));
        $plan = $this->api()->get('me/itinerary', ['limit' => $planDays]);

        return view('recommendations.index', [
            'matched' => $rec['data']['matched'] ?? [],
            'explore' => $rec['data']['explore'] ?? [],
            'profile' => $rec['data']['profile'] ?? [],
            'itinerary' => $plan['data']['itinerary'] ?? [],
            'totalMatch' => $plan['data']['total_match'] ?? 0,
            'planDays' => $planDays,
            'favoriteIds' => $this->favoriteIds(),
        ]);
    }
}
