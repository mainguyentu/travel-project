<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class HomeController extends BaseController
{
    public function index()
    {
        $body = $this->api()->get('public/landing');
        $landing = $body['data'] ?? ['highlights' => [], 'categories' => [], 'top_ratings' => [], 'top_favorites' => []];

        return view('home', ['landing' => $landing]);
    }
}
