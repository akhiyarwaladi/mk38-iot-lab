<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Actuator extends Model
{
    protected $dateFormat = 'Y-m-d H:i:s.v';
    protected $fillable = ['device_id', 'name', 'kind', 'requested_value', 'reported_value',
        'boot_id', 'report_sequence', 'reported_at'];

    protected function casts(): array
    {
        return ['requested_value' => 'integer', 'reported_value' => 'integer',
            'report_sequence' => 'integer', 'reported_at' => 'datetime'];
    }
}
