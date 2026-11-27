<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class ProfileController extends BaseController
{
    public function profile()
    {
        return view('profile', ['user' => session('user')]);
    }

    public function favorites(Request $request)
    {
        $page = max(1, (int) $request->input('page', 1));
        $body = $this->api()->get('me/favorites', ['page' => $page, 'limit' => 20]);

        return view('favorites', [
            'destinations' => $body['data'] ?? [],
            'meta' => $body['meta'] ?? ['page' => $page, 'limit' => 20],
        ]);
    }

    public function addFavorite(int $id)
    {
        $this->api()->post("me/favorites/{$id}");

        return back()->with('status', 'Đã thêm vào yêu thích.');
    }

    public function removeFavorite(int $id)
    {
        $this->api()->delete("me/favorites/{$id}");

        return back()->with('status', 'Đã xóa khỏi yêu thích.');
    }

    public function rate(Request $request, int $id)
    {
        $data = $request->validate([
            'rating_score' => 'required|integer|min:1|max:5',
            'comment' => 'nullable|string|max:1000',
        ]);
        $body = $this->api()->put("me/ratings/{$id}", $data);
        if (($body['_status'] ?? 500) !== 200) {
            return back()->with('error', $this->apiError($body, 'Đánh giá thất bại.'));
        }

        return back()->with('status', 'Đã lưu đánh giá.');
    }
}
