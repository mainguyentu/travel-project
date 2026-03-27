<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Session;

class AdminAuthenticate
{
    /**
     * Handle an incoming request.
     */
    public function handle(Request $request, Closure $next)
    {
        if (!Session::has('access_token')) {
            return redirect('/login');
        }

        $user = Session::get('user');
        if (!is_array($user) || ($user['role'] ?? null) !== 'admin') {
            abort(403, 'Unauthorized');
        }

        return $next($request);
    }
}
