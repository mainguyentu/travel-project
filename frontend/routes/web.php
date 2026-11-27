<?php

use App\Http\Controllers\AdminController;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\DestinationController;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\ProfileController;
use Illuminate\Support\Facades\Route;

Route::get('/', [HomeController::class, 'index'])->name('home');
Route::get('/destinations', [DestinationController::class, 'index'])->name('destinations.index');
Route::get('/activities/{slug}', [AdminController::class, 'activityRecommendations'])->name('activities.show');

Route::middleware('guest.only')->group(function () {
    Route::get('/login', [AuthController::class, 'showLogin'])->name('login');
    Route::post('/login', [AuthController::class, 'login']);
    Route::get('/register', [AuthController::class, 'showRegister'])->name('register');
    Route::post('/register', [AuthController::class, 'register']);
});

Route::middleware('session.auth')->group(function () {
    Route::post('/logout', [AuthController::class, 'logout'])->name('logout');
    Route::get('/profile', [ProfileController::class, 'profile'])->name('profile.index');
    Route::get('/my-favorites', [ProfileController::class, 'favorites'])->name('favorites.index');
    Route::post('/favorites/{id}', [ProfileController::class, 'addFavorite'])->name('favorites.add');
    Route::delete('/favorites/{id}', [ProfileController::class, 'removeFavorite'])->name('favorites.remove');
    Route::put('/ratings/{id}', [ProfileController::class, 'rate'])->name('ratings.store');
});

Route::middleware('session.admin')->prefix('admin')->name('admin.')->group(function () {
    Route::get('/', [AdminController::class, 'dashboard'])->name('dashboard');
    Route::get('/users', [AdminController::class, 'users'])->name('users.index');
    Route::patch('/users/{id}/status', [AdminController::class, 'updateUserStatus'])->name('users.status');
    Route::patch('/users/{id}/role', [AdminController::class, 'updateUserRole'])->name('users.role');
    Route::get('/categories', [AdminController::class, 'categories'])->name('categories.index');
    Route::post('/categories', [AdminController::class, 'storeCategory'])->name('categories.store');
    Route::put('/categories/{id}', [AdminController::class, 'updateCategory'])->name('categories.update');
    Route::delete('/categories/{id}', [AdminController::class, 'deleteCategory'])->name('categories.delete');
    Route::get('/destinations', [AdminController::class, 'destinations'])->name('destinations.index');
    Route::post('/destinations', [AdminController::class, 'storeDestination'])->name('destinations.store');
    Route::post('/destinations/bulk', [AdminController::class, 'bulkStoreDestinations'])->name('destinations.bulk');
    Route::put('/destinations/{id}', [AdminController::class, 'updateDestination'])->name('destinations.update');
    Route::delete('/destinations/{id}', [AdminController::class, 'deleteDestination'])->name('destinations.delete');
    Route::get('/stats', [AdminController::class, 'stats'])->name('stats.index');
    Route::get('/audit-logs', [AdminController::class, 'auditLogs'])->name('audit-logs.index');
});
