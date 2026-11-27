<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class AuthController extends BaseController
{
    public function showLogin()
    {
        return view('auth.login');
    }

    public function login(Request $request)
    {
        $data = $request->validate([
            'email' => 'required|email',
            'password' => 'required|string',
        ]);

        $body = $this->api()->post('auth/login', $data);
        if (($body['_status'] ?? 500) !== 200) {
            return back()->withInput($request->only('email'))->with('error', $this->apiError($body, 'Đăng nhập thất bại.'));
        }

        session([
            'access_token' => $body['data']['access_token'],
            'refresh_token' => $body['data']['refresh_token'],
        ]);

        // Role probe: admin khi đọc được admin stats.
        $probe = $this->api()->get('admin/stats/top-views');
        session(['is_admin' => ($probe['_status'] ?? 403) === 200]);

        $me = null;
        // Lấy email làm định danh hiển thị (backend MVP chưa có /me/profile).
        session(['user' => ['email' => $data['email']]]);

        return redirect()->intended(session('is_admin') ? '/admin' : '/');
    }

    public function showRegister()
    {
        return view('auth.register');
    }

    public function register(Request $request)
    {
        $data = $request->validate([
            'name' => 'required|string|max:120',
            'email' => 'required|email',
            'password' => 'required|string|min:8|max:128|confirmed',
        ]);
        unset($data['password_confirmation']);

        $body = $this->api()->post('auth/register', $data);
        if (($body['_status'] ?? 500) !== 201) {
            return back()->withInput($request->only('name', 'email'))->with('error', $this->apiError($body, 'Đăng ký thất bại.'));
        }

        return redirect()->route('login')->with('status', 'Đăng ký thành công, mời đăng nhập.');
    }

    public function logout(Request $request)
    {
        $refresh = session('refresh_token');
        if ($refresh) {
            try {
                $this->api()->post('auth/logout', ['refresh_token' => $refresh]);
            } catch (\Throwable $e) {
                // Logout best-effort: luôn xóa session local.
            }
        }
        session()->forget(['access_token', 'refresh_token', 'user', 'is_admin']);

        return redirect()->route('home');
    }
}
