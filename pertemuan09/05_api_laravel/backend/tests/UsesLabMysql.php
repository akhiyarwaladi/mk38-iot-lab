<?php

namespace Tests;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\DB;

trait UsesLabMysql
{
    use RefreshDatabase;

    protected function beforeRefreshingDatabase(): void
    {
        if (DB::connection()->getDriverName() !== 'mysql'
            || DB::connection()->getDatabaseName() !== 'mk38_sensor_test') {
            throw new \RuntimeException('Uji hanya boleh memakai MySQL mk38_sensor_test.');
        }
    }
}
