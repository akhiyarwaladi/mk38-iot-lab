<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Sensor extends Model
{
    protected $fillable = ['device_id', 'suhu', 'kelembapan'];

    protected $hidden = ['updated_at'];

    protected function casts(): array
    {
        return ['suhu' => 'float', 'kelembapan' => 'float'];
    }
}

