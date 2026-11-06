<?php

namespace Tests\Feature;

use Tests\UsesLabMysql;
use Tests\TestCase;

class SensorApiTest extends TestCase
{
    use UsesLabMysql;

    public function test_post_commits_the_values_returned_to_the_client(): void
    {
        $saved = $this->postJson('/api/v1/sensor', [
            'device_id' => 'esp32-01', 'suhu' => 28.567, 'kelembapan' => 65,
        ])->assertCreated()->assertJsonPath('suhu', 28.6);
        $id = $saved->json('id');
        $saved->assertHeader('Location', '/api/v1/sensor/'.$id);
        $this->assertDatabaseHas('sensors', [
            'id' => $id, 'device_id' => 'esp32-01', 'suhu' => 28.6, 'kelembapan' => 65,
        ]);
        $this->getJson('/api/v1/sensor/'.$id)->assertOk()
            ->assertExactJson($saved->json());
    }

    public function test_invalid_payloads_are_rejected_without_creating_rows(): void
    {
        $valid = ['device_id' => 'esp32-01', 'suhu' => 28, 'kelembapan' => 65];
        foreach ([[], [...$valid, 'kelembapan' => 101], [...$valid, 'suhu' => -41],
                  [...$valid, 'suhu' => null], [...$valid, 'suhu' => true],
                  [...$valid, 'suhu' => 'bukan angka'], [...$valid, 'device_id' => ''],
                  [...$valid, 'device_id' => "x'; DROP TABLE sensors;--"]] as $body) {
            $this->postJson('/api/v1/sensor', $body)->assertUnprocessable();
        }
        $this->assertDatabaseCount('sensors', 0);
    }

    public function test_list_supports_device_filter_latest_first_and_limit(): void
    {
        $this->getJson('/api/v1/sensor')->assertOk()->assertExactJson([]);
        foreach ([['esp32-01', 25], ['esp32-02', 28], ['esp32-01', 30]] as [$id, $suhu]) {
            $this->postJson('/api/v1/sensor', [
                'device_id' => $id, 'suhu' => $suhu, 'kelembapan' => 60,
            ])->assertCreated();
        }
        $this->getJson('/api/v1/sensor?device_id=esp32-01&limit=1')
            ->assertOk()->assertJsonCount(1)->assertJsonPath('0.suhu', 30);
        $this->getJson('/api/v1/sensor/999999')->assertNotFound();
        foreach (['0', '101', 'abc'] as $limit) {
            $this->getJson('/api/v1/sensor?limit='.$limit)->assertUnprocessable();
        }
    }

    public function test_unknown_fields_cannot_set_the_database_id(): void
    {
        $saved = $this->postJson('/api/v1/sensor', [
            'id' => 9000, 'device_id' => 'esp32-01', 'suhu' => 28, 'kelembapan' => 60,
        ])->assertCreated();
        $this->assertNotEquals(9000, $saved->json('id'));
    }

    public function test_health_and_api_errors_do_not_require_browser_headers(): void
    {
        $this->get('/')->assertOk()->assertJsonPath('sensor', '/api/v1/sensor');
        $this->get('/api/v1/health')->assertOk()->assertJsonPath('status', 'ok');
        $this->post('/api/v1/sensor', [])->assertUnprocessable()->assertJsonValidationErrors('suhu');
    }

    public function test_progressive_routes_receive_data_before_database_writes(): void
    {
        foreach (['01_api_health.php', '02_api_terima.php'] as $stage) {
            $this->app['router']->setRoutes(new \Illuminate\Routing\RouteCollection);
            \Illuminate\Support\Facades\Route::middleware('api')->prefix('api')
                ->group(base_path('../tahapan/'.$stage));
            $this->getJson('/api/v1/health')->assertOk()->assertJsonPath('status', 'ok');
            $body = ['device_id' => 'esp32-01', 'suhu' => 28, 'kelembapan' => 65];
            if ($stage === '01_api_health.php') {
                $this->postJson('/api/v1/sensor', $body)->assertNotFound();
            } else {
                $this->postJson('/api/v1/sensor', $body)->assertOk()
                    ->assertJsonPath('tersimpan', false)->assertJsonPath('diterima.suhu', 28);
            }
            $this->assertDatabaseCount('sensors', 0);
        }
    }
}
