<?php

namespace App\Providers;

use Illuminate\Support\Facades\Route;
use Illuminate\Support\ServiceProvider;

class ActuatorServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        if (! $this->app->routesAreCached()) {
            Route::middleware('api')->prefix('api/v1')->group(base_path('routes/actuators.php'));
            Route::middleware('web')->get('/aktuator', fn () => view('actuators'));
        }
    }
}
