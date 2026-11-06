<?php

require __DIR__.'/../vendor/autoload.php';
$app = require __DIR__.'/../bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();

$db = Illuminate\Support\Facades\DB::connection();
$result = [
    'driver' => $db->getDriverName(),
    'server_version' => $db->selectOne('SELECT VERSION() AS version')->version,
    'database' => $db->getDatabaseName(),
    'count' => $db->table('sensors')->count(),
    'examples' => $db->table('sensors')->selectRaw('MIN(id) AS id, suhu, kelembapan')
        ->groupBy('suhu', 'kelembapan')->orderBy('id')->get()->toArray(),
    'rows' => $db->table('sensors')->orderByDesc('id')->limit(5)->get()->toArray(),
    'devices' => $db->table('devices')->orderBy('device_id')->get()->toArray(),
    'commands' => $db->table('commands')->orderByDesc('id')->limit(10)->get()->toArray(),
];
echo json_encode($result, JSON_PRETTY_PRINT | JSON_THROW_ON_ERROR).PHP_EOL;
