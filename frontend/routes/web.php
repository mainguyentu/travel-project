<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\DestinationController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\ProfileController;
use App\Http\Controllers\AdminController;

// Public routes
Route::get('/', [HomeController::class, 'index'])->name('home');

// Destination routes
Route::get('/destinations', [DestinationController::class, 'index'])->name('destinations.index');
Route::get('/destinations/{destinationId}', [DestinationController::class, 'show'])->name('destinations.show');

// Auth routes
Route::middleware('guest')->group(function () {
    Route::get('/login', [AuthController::class, 'showLogin'])->name('login');
    Route::post('/login', [AuthController::class, 'login']);
    
    Route::get('/register', [AuthController::class, 'showRegister'])->name('register');
    Route::post('/register', [AuthController::class, 'register']);
});

Route::post('/logout', [AuthController::class, 'logout'])->name('logout')->middleware('session.auth');

// User routes
Route::middleware('session.auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'index'])->name('profile.index');
    Route::get('/my-favorites', [ProfileController::class, 'favorites'])->name('favorites.index');
    
    Route::post('/favorites/{destinationId}', [ProfileController::class, 'addFavorite'])->name('favorites.add');
    Route::delete('/favorites/{destinationId}', [ProfileController::class, 'removeFavorite'])->name('favorites.remove');
    
    Route::put('/ratings/{destinationId}', [ProfileController::class, 'rate'])->name('ratings.store');
});

// Admin routes
Route::middleware('session.admin')->prefix('admin')->group(function () {
    Route::get('/', [AdminController::class, 'dashboard'])->name('admin.dashboard');
    Route::get('/users', [AdminController::class, 'users'])->name('admin.users.index');
    Route::get('/categories', [AdminController::class, 'categories'])->name('admin.categories.index');
    Route::get('/destinations', [AdminController::class, 'destinations'])->name('admin.destinations.index');
    Route::get('/stats', [AdminController::class, 'stats'])->name('admin.stats.index');
});
