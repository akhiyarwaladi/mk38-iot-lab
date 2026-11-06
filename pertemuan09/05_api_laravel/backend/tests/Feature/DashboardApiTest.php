<?php

namespace Tests\Feature;

use App\Models\Device;
use Tests\TestCase;
use Tests\UsesLabMysql;

class DashboardApiTest extends TestCase
{
    use UsesLabMysql;

    private function sample(string $id = 'esp32-01', float $temperature = 32): void
    {
        $this->postJson('/api/v1/sensor', ['device_id' => $id,
            'suhu' => $temperature, 'kelembapan' => 65])->assertCreated();
    }

    public function test_empty_dashboard_and_unknown_device_are_truthful(): void
    {
        $this->get('/dashboard')->assertOk();
        $this->getJson('/api/v1/pemantauan')->assertOk()->assertJsonPath('online', false)
            ->assertJsonPath('latest', null)->assertJsonCount(0, 'readings');
        $this->getJson('/api/v1/pemantauan?device_id=belum-ada')->assertOk()
            ->assertJsonPath('device', null)->assertJsonCount(0, 'commands');
    }

    public function test_threshold_warning_staleness_and_device_filter(): void
    {
        $this->sample();
        $this->sample('esp32-02', 20);
        $this->getJson('/api/v1/pemantauan?device_id=esp32-01&limit=1')->assertOk()
            ->assertJsonPath('online', true)->assertJsonPath('warning', true)
            ->assertJsonCount(1, 'readings')->assertJsonPath('latest.device_id', 'esp32-01');
        $this->putJson('/api/v1/perangkat/esp32-01/pengaturan', ['suhu_batas' => 35])->assertOk();
        $this->getJson('/api/v1/pemantauan?device_id=esp32-01')->assertJsonPath('warning', false);
        $this->travel(31)->seconds();
        $this->getJson('/api/v1/pemantauan?device_id=esp32-01')->assertJsonPath('online', false);
        $this->travelBack();
        $this->putJson('/api/v1/perangkat/esp32-01/pengaturan', ['suhu_batas' => 81])->assertUnprocessable();
        $this->getJson('/api/v1/pemantauan?limit=101')->assertUnprocessable();
    }

    public function test_csv_matches_the_selected_device_and_limit(): void
    {
        $this->sample();
        $this->sample('esp32-02', 20);
        $this->sample('esp32-01', 35);
        $snapshotId = \App\Models\Sensor::max('id');
        $this->sample('esp32-01', 40);
        $response = $this->get('/api/v1/ekspor.csv?device_id=esp32-01&limit=1&until_id='.$snapshotId)->assertOk()
            ->assertHeader('Content-Type', 'text/csv; charset=UTF-8');
        $lines = array_map('str_getcsv', explode("\n", trim($response->streamedContent())));
        $this->assertCount(2, $lines);
        $this->assertSame(['id', 'device_id', 'suhu_celsius', 'kelembapan_persen', 'diterima_utc'], $lines[0]);
        $this->assertSame('esp32-01', $lines[1][1]);
        $this->assertEquals(35, $lines[1][2]);
        $this->get('/api/v1/ekspor.csv?device_id=belum-ada')->assertOk();
    }

    public function test_command_waits_for_matching_device_confirmation(): void
    {
        $this->sample();
        $this->postJson('/api/v1/perangkat/esp32-01/status', ['led' => false])->assertOk();
        $command = $this->postJson('/api/v1/perangkat/esp32-01/perintah', ['led' => true])
            ->assertStatus(202)->assertJsonPath('status', 'pending')->json();
        $this->assertFalse(Device::find('esp32-01')->led);
        $this->getJson('/api/v1/perangkat/esp32-01/perintah')->assertJsonPath('command.id', $command['id']);
        $this->postJson('/api/v1/perangkat/esp32-01/konfirmasi', ['command_id' => $command['id'], 'led' => false])
            ->assertUnprocessable();
        $ack = $this->postJson('/api/v1/perangkat/esp32-01/konfirmasi', ['command_id' => $command['id'], 'led' => true])
            ->assertOk()->assertJsonPath('status', 'applied')->json();
        $this->assertTrue(Device::find('esp32-01')->led);
        $this->postJson('/api/v1/perangkat/esp32-01/konfirmasi', ['command_id' => $command['id'], 'led' => true])
            ->assertExactJson($ack);
        $this->getJson('/api/v1/perangkat/esp32-01/perintah')->assertJsonPath('command', null);
    }

    public function test_superseded_expired_and_foreign_commands_cannot_be_acknowledged(): void
    {
        $this->sample(); $this->sample('esp32-02');
        $first = $this->postJson('/api/v1/perangkat/esp32-01/perintah', ['led' => true])->json('id');
        $second = $this->postJson('/api/v1/perangkat/esp32-01/perintah', ['led' => false])->json('id');
        $this->postJson('/api/v1/perangkat/esp32-01/konfirmasi', ['command_id' => $first, 'led' => true])->assertStatus(409);
        $this->postJson('/api/v1/perangkat/esp32-02/konfirmasi', ['command_id' => $second, 'led' => false])->assertNotFound();
        $this->travel(31)->seconds();
        $this->getJson('/api/v1/perangkat/esp32-01/perintah')->assertJsonPath('command', null);
        $this->postJson('/api/v1/perangkat/esp32-01/konfirmasi', ['command_id' => $second, 'led' => false])->assertStatus(409);
        $this->getJson('/api/v1/pemantauan?device_id=esp32-01')->assertJsonPath('commands.0.status', 'expired')
            ->assertJsonPath('commands.1.status', 'superseded');
        $this->travelBack();
        $this->assertNull(Device::find('esp32-01')->led);
    }

    public function test_old_ack_retry_does_not_overwrite_newer_reported_state(): void
    {
        $this->sample();
        $id = $this->postJson('/api/v1/perangkat/esp32-01/perintah', ['led' => true])->json('id');
        $this->postJson('/api/v1/perangkat/esp32-01/konfirmasi', ['command_id' => $id, 'led' => true])->assertOk();
        $this->postJson('/api/v1/perangkat/esp32-01/status', ['led' => false])->assertOk();
        $this->postJson('/api/v1/perangkat/esp32-01/konfirmasi', ['command_id' => $id, 'led' => true])->assertOk();
        $this->assertFalse(Device::find('esp32-01')->led);
    }
}
