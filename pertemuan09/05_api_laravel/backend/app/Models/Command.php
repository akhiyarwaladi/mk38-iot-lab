<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Command extends Model
{
    protected $dateFormat = 'Y-m-d H:i:s.v';
    protected $fillable = ['device_id', 'led', 'status', 'expires_at', 'acknowledged_at'];

    protected function casts(): array
    {
        return ['led' => 'boolean', 'expires_at' => 'datetime', 'acknowledged_at' => 'datetime'];
    }

    public function result(): array
    {
        $result = $this->toArray();
        if ($this->status === 'pending' && $this->expires_at->isPast()) {
            $result['status'] = 'expired';
        }
        return $result;
    }
}
