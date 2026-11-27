<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class AdminController extends BaseController
{
    public function dashboard(Request $request)
    {
        $api = $this->api();
        $query = array_filter([
            'from' => $request->input('from'),
            'to' => $request->input('to'),
        ]);
        $fav = $api->get('admin/stats/top-favorites', ['limit' => 10] + $query);
        $ratings = $api->get('admin/stats/top-ratings', ['limit' => 10] + $query);
        $views = $api->get('admin/stats/top-views', ['limit' => 10]);

        return view('admin.dashboard', [
            'topFavorites' => $fav['data'] ?? [],
            'topRatings' => $ratings['data'] ?? [],
            'topViews' => $views['data'] ?? [],
            'from' => $request->input('from'),
            'to' => $request->input('to'),
            'searchEngine' => $views['meta']['search_engine'] ?? $fav['meta']['search_engine'] ?? 'DB',
        ]);
    }

    public function stats(Request $request)
    {
        $api = $this->api();
        $query = array_filter([
            'from' => $request->input('from'),
            'to' => $request->input('to'),
        ]);
        $fav = $api->get('admin/stats/top-favorites', ['limit' => 10] + $query);
        $ratings = $api->get('admin/stats/top-ratings', ['limit' => 10] + $query);
        $views = $api->get('admin/stats/top-views', ['limit' => 10]);

        return view('admin.stats', [
            'topFavorites' => $fav['data'] ?? [],
            'topRatings' => $ratings['data'] ?? [],
            'topViews' => $views['data'] ?? [],
            'searchEngine' => $views['meta']['search_engine'] ?? $fav['meta']['search_engine'] ?? 'DB',
        ]);
    }

    public function users(Request $request)
    {
        $page = max(1, (int) $request->input('page', 1));
        $body = $this->api()->get('admin/users', ['page' => $page, 'limit' => 20]);

        return view('admin.users.index', [
            'users' => $body['data'] ?? [],
            'meta' => $body['meta'] ?? ['page' => $page, 'limit' => 20, 'total' => 0],
        ]);
    }

    public function updateUserStatus(Request $request, int $id)
    {
        $data = $request->validate(['status' => 'required|in:active,locked']);
        $this->api()->patch("admin/users/{$id}/status", $data);

        return back()->with('status', 'Đã cập nhật trạng thái user.');
    }

    public function updateUserRole(Request $request, int $id)
    {
        $data = $request->validate(['role' => 'required|in:user,admin']);
        $this->api()->patch("admin/users/{$id}/role", $data);

        return back()->with('status', 'Đã cập nhật role user.');
    }

    public function categories()
    {
        $body = $this->api()->get('admin/categories');

        return view('admin.categories.index', ['categories' => $body['data'] ?? []]);
    }

    public function storeCategory(Request $request)
    {
        $data = $request->validate([
            'name' => 'required|string|max:120',
            'slug' => 'required|string|max:160',
            'descriptions' => 'nullable|string',
        ]);
        $body = $this->api()->post('admin/categories', $data);
        if (($body['_status'] ?? 500) !== 201) {
            return back()->withInput()->with('error', $this->apiError($body, 'Tạo category thất bại.'));
        }

        return back()->with('status', 'Đã tạo category.');
    }

    public function updateCategory(Request $request, int $id)
    {
        $data = $request->validate([
            'name' => 'nullable|string|max:120',
            'slug' => 'nullable|string|max:160',
            'descriptions' => 'nullable|string',
        ]);
        $this->api()->put("admin/categories/{$id}", array_filter($data, fn ($v) => $v !== null));

        return back()->with('status', 'Đã cập nhật category.');
    }

    public function deleteCategory(int $id)
    {
        $this->api()->delete("admin/categories/{$id}");

        return back()->with('status', 'Đã xóa category.');
    }

    public function destinations(Request $request)
    {
        $page = max(1, (int) $request->input('page', 1));
        $body = $this->api()->get('admin/destinations', [
            'page' => $page,
            'limit' => 20,
            'status' => $request->input('status'),
            'keyword' => $request->input('keyword'),
        ]);

        return view('admin.destinations.index', [
            'destinations' => $body['data'] ?? [],
            'meta' => $body['meta'] ?? ['page' => $page, 'limit' => 20, 'total' => 0],
        ]);
    }

    public function storeDestination(Request $request)
    {
        $data = $request->validate([
            'name' => 'required|string|max:180',
            'slug' => 'required|string|max:220',
            'address' => 'nullable|string',
            'description' => 'nullable|string',
            'price_level' => 'required|in:free,low,medium,high',
            'open_hour' => 'nullable|string|max:120',
            'img_url' => 'nullable|string',
            'url_map' => 'nullable|string',
            'status' => 'nullable|in:active,inactive',
            'category_slugs' => 'nullable|string',
        ]);
        $data['category_slugs'] = $data['category_slugs'] !== null && $data['category_slugs'] !== ''
            ? array_values(array_filter(array_map('trim', explode(',', $data['category_slugs']))))
            : [];
        $body = $this->api()->post('admin/destinations', $data);
        if (($body['_status'] ?? 500) !== 201) {
            return back()->withInput()->with('error', $this->apiError($body, 'Tạo destination thất bại.'));
        }

        return back()->with('status', 'Đã tạo destination.');
    }

    public function updateDestination(Request $request, int $id)
    {
        $data = $request->validate([
            'name' => 'nullable|string|max:180',
            'slug' => 'nullable|string|max:220',
            'price_level' => 'nullable|in:free,low,medium,high',
            'status' => 'nullable|in:active,inactive',
            'address' => 'nullable|string',
            'description' => 'nullable|string',
        ]);
        $this->api()->put("admin/destinations/{$id}", array_filter($data, fn ($v) => $v !== null));

        return back()->with('status', 'Đã cập nhật destination.');
    }

    public function deleteDestination(int $id)
    {
        $this->api()->delete("admin/destinations/{$id}");

        return back()->with('status', 'Đã xóa destination.');
    }

    public function bulkStoreDestinations(Request $request)
    {
        $data = $request->validate([
            'payload' => 'required|string',
        ]);
        $items = json_decode($data['payload'], true);
        if (! is_array($items)) {
            return back()->withInput()->with('error', 'JSON không hợp lệ: cần mảng items.');
        }
        $body = $this->api()->post('admin/destinations/bulk', ['items' => array_values($items)]);
        if (($body['_status'] ?? 500) !== 201) {
            return back()->withInput()->with('error', $this->apiError($body, 'Bulk import thất bại.'));
        }

        return back()->with('status', 'Đã bulk import '.count($body['data'] ?? []).' destinations.');
    }

    public function auditLogs(Request $request)
    {
        $page = max(1, (int) $request->input('page', 1));
        $body = $this->api()->get('admin/audit-logs', ['page' => $page, 'limit' => 20]);

        return view('admin.audit-logs', [
            'logs' => $body['data'] ?? [],
            'meta' => $body['meta'] ?? ['page' => $page, 'limit' => 20, 'total' => 0],
        ]);
    }

    public function activityRecommendations(string $slug, Request $request)
    {
        $body = $this->api()->get("public/activities/{$slug}/recommendations", [
            'page' => max(1, (int) $request->input('page', 1)),
            'limit' => 10,
            'budget_level' => $request->input('budget_level'),
        ]);
        if (($body['_status'] ?? 500) !== 200) {
            abort(404);
        }

        return view('activities.show', ['payload' => $body['data'] ?? []]);
    }
}
