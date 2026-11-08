<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ActuatorStateEvent extends Model
{
    public const UPDATED_AT = null;
    protected $dateFormat = 'Y-m-d H:i:s.v';
    protected $fillable = ['actuator_id', 'command_id', 'value', 'reason', 'boot_id', 'sequence'];

    protected function casts(): array
    {
        return ['value' => 'integer', 'sequence' => 'integer', 'created_at' => 'datetime'];
    }
}
