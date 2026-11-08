<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ActuatorCommand extends Model
{
    protected $dateFormat = 'Y-m-d H:i:s.v';
    protected $fillable = ['actuator_id', 'value', 'status', 'expires_at', 'acknowledged_at'];

    protected function casts(): array
    {
        return ['value' => 'integer', 'expires_at' => 'datetime', 'acknowledged_at' => 'datetime'];
    }
}
