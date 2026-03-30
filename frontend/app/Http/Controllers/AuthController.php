<?php

namespace App\Http\Controllers;

use App\Http\Requests\LoginRequest;
use App\Http\Requests\RegisterRequest;
use App\Services\ApiClient;
use Illuminate\Support\Facades\Session;

class AuthController extends Controller
{
    private ApiClient $apiClient;

    public function __construct(ApiClient $apiClient)
    {
        $this->apiClient = $apiClient;
    }

    /**
     * Show login form
     */
    public function showLogin()
    {
        if (Session::has('access_token')) {
            return redirect('/profile');
        }
        
        return view('pages.public.auth.login');
    }

    /**
     * Handle login
     */
    public function login(LoginRequest $request)
    {
        $validated = $request->validated();

        $response = $this->apiClient->post('auth/login', [
            'email' => $validated['email'],
            'password' => $validated['password'],
        ]);

        if (!($response['success'] ?? false)) {
            $apiError = $response['error'] ?? 'Thông tin xác thực không hợp lệ';
            return back()
                ->withInput($request->only('email'))
                ->withErrors([
                    'email' => 'Email hoặc mật khẩu chưa đúng.',
                    'api' => $apiError,
                ]);
        }

        // Store tokens in session
        Session::put('access_token', $response['data']['access_token']);
        Session::put('refresh_token', $response['data']['refresh_token']);

        $user = [
            'email' => $validated['email'],
            'name' => $validated['email'],
            'role' => 'user',
            'is_admin' => false,
        ];

        // Probe admin endpoint to infer admin role from current token.
        $adminProbe = $this->apiClient->get('admin/stats/top-views');
        if (($adminProbe['success'] ?? false) === true) {
            $user['role'] = 'admin';
            $user['is_admin'] = true;
        }

        Session::put('user', $user);

        return redirect('/profile');
    }

    /**
     * Show register form
     */
    public function showRegister()
    {
        if (Session::has('access_token')) {
            return redirect('/profile');
        }
        
        return view('pages.public.auth.register');
    }

    /**
     * Handle registration
     */
    public function register(RegisterRequest $request)
    {
        $validated = $request->validated();

        $response = $this->apiClient->post('auth/register', [
            'name' => $validated['name'],
            'email' => $validated['email'],
            'password' => $validated['password'],
        ]);

        if (!($response['success'] ?? false)) {
            $details = $response['details'] ?? [];
            $errors = is_array($details) && $details !== []
                ? $details
                : ['api' => ($response['error'] ?? 'Không thể đăng ký tài khoản lúc này.')];

            return back()
                ->withInput($request->except('password', 'password_confirmation'))
                ->withErrors($errors);
        }

        return redirect('/login')->with('success', 'Đăng ký thành công. Vui lòng đăng nhập.');
    }

    /**
     * Handle logout
     */
    public function logout()
    {
        $refreshToken = Session::get('refresh_token');
        if ($refreshToken) {
            $this->apiClient->post('auth/logout', ['refresh_token' => $refreshToken]);
        }

        Session::forget(['access_token', 'refresh_token', 'user']);
        
        return redirect('/');
    }
}
