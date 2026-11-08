<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('actuators', function (Blueprint $table) {
            $table->id();
            $table->string('device_id', 40);
            $table->foreign('device_id')->references('device_id')->on('devices');
            $table->string('name', 32);
            $table->string('kind', 8);
            $table->unsignedSmallInteger('requested_value')->nullable();
            $table->unsignedSmallInteger('reported_value')->nullable();
            $table->string('boot_id', 16)->nullable();
            $table->unsignedInteger('report_sequence')->default(0);
            $table->timestamp('reported_at', 3)->nullable();
            $table->timestamps(3);
            $table->unique(['device_id', 'name']);
        });
        Schema::create('actuator_commands', function (Blueprint $table) {
            $table->id();
            $table->foreignId('actuator_id')->constrained();
            $table->unsignedSmallInteger('value');
            $table->string('status', 16)->default('pending');
            $table->timestamp('expires_at', 3);
            $table->timestamp('acknowledged_at', 3)->nullable();
            $table->timestamps(3);
            $table->index(['actuator_id', 'id']);
        });
        Schema::create('actuator_state_events', function (Blueprint $table) {
            $table->id();
            $table->foreignId('actuator_id')->constrained();
            $table->foreignId('command_id')->nullable()->constrained('actuator_commands');
            $table->unsignedSmallInteger('value');
            $table->string('reason', 16);
            $table->string('boot_id', 16);
            $table->unsignedInteger('sequence');
            $table->timestamp('created_at', 3);
            $table->unique('command_id');
            $table->unique(['actuator_id', 'boot_id', 'sequence'], 'actuator_event_sequence');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('actuator_state_events');
        Schema::dropIfExists('actuator_commands');
        Schema::dropIfExists('actuators');
    }
};
