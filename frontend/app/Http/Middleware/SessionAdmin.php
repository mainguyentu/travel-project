<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;

class SessionAdmin
{
    public function handle(Request $request, Closure $next)
    {
        if (! session('access_token')) {
            return redirect()->route('login');
        }
        if (! session('is_admin')) {
            abort(403, 'Admin only.');
        }

        return $next($request);
    }
}
