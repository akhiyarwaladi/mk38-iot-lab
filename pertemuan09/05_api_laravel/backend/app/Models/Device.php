<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Device extends Model
{
    protected $primaryKey = 'device_id';
    public $incrementing = false;
    protected $keyType = 'string';
    protected $dateFormat = 'Y-m-d H:i:s.v';
    protected $fillable = ['device_id', 'suhu_batas', 'led', 'reported_at'];

    protected function casts(): array
    {
        return ['suhu_batas' => 'float', 'led' => 'boolean', 'reported_at' => 'datetime'];
    }
}
