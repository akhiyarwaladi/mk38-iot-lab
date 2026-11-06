<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('devices', function (Blueprint $table) {
            $table->string('device_id', 40)->primary();
            $table->decimal('suhu_batas', 4, 1)->default(30);
            $table->boolean('led')->nullable();
            $table->timestamp('reported_at', 3)->nullable();
            $table->timestamps(3);
        });
        Schema::create('commands', function (Blueprint $table) {
            $table->id();
            $table->string('device_id', 40);
            $table->foreign('device_id')->references('device_id')->on('devices');
            $table->boolean('led');
            $table->string('status', 16)->default('pending');
            $table->timestamp('expires_at', 3);
            $table->timestamp('acknowledged_at', 3)->nullable();
            $table->timestamps(3);
            $table->index(['device_id', 'id']);
        });
        foreach (DB::table('sensors')->distinct()->pluck('device_id') as $id) {
            DB::table('devices')->insert(['device_id' => $id, 'created_at' => now(), 'updated_at' => now()]);
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('commands');
        Schema::dropIfExists('devices');
    }
};
