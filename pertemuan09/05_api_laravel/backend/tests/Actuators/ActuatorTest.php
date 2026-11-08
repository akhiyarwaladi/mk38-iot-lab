<?php

namespace Tests\Actuators;

use App\Models\Actuator;
use App\Models\ActuatorCommand;
use App\Models\ActuatorStateEvent;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ActuatorTest extends TestCase
{
    use RefreshDatabase;

    private const BOOT = '1234567890abcdef';

    private function register(string $name = 'lampu', string $kind = 'led'): int
    {
        return $this->postJson('/api/v1/aktuator', ['device_id' => 'uji-aktuator',
            'name' => $name, 'kind' => $kind])->assertCreated()->json('id');
    }

    private function boot(int $id, string $boot = self::BOOT): void
    {
        $this->postJson("/api/v1/aktuator/{$id}/status", ['value' => 0, 'boot_id' => $boot,
            'sequence' => 1, 'reason' => 'boot'])->assertOk();
    }

    private function command(int $id, int $value): int
    {
        return $this->postJson("/api/v1/aktuator/{$id}/perintah", ['value' => $value])
            ->assertAccepted()->json('id');
    }

    private function ack(int $id, int $command, int $value, int $sequence = 2, string $boot = self::BOOT)
    {
        return $this->postJson("/api/v1/aktuator/{$id}/konfirmasi", ['command_id' => $command,
            'value' => $value, 'boot_id' => $boot, 'sequence' => $sequence]);
    }

    public function test_registration_does_not_need_sensor_readings(): void
    {
        $id = $this->register();
        $this->assertDatabaseCount('sensors', 0);
        $this->assertDatabaseHas('devices', ['device_id' => 'uji-aktuator']);
        $this->postJson('/api/v1/aktuator', ['device_id' => 'uji-aktuator', 'name' => 'lampu', 'kind' => 'led'])
            ->assertOk()->assertJsonPath('id', $id);
        $this->assertDatabaseCount('actuators', 1);
        $this->postJson('/api/v1/aktuator', ['device_id' => 'uji-aktuator', 'name' => 'lampu', 'kind' => 'servo'])->assertConflict();
        $this->getJson('/api/v1/aktuator?device_id=belum-ada')->assertExactJson([]);
    }

    public function test_registration_and_values_are_validated(): void
    {
        $this->postJson('/api/v1/aktuator', ['device_id' => '../bad', 'name' => 'x', 'kind' => 'relay'])->assertUnprocessable();
        $led = $this->register();
        $servo = $this->register('pintu', 'servo');
        foreach ([-1, 2, 180, '1', true, null, 0.5] as $value) {
            $this->postJson("/api/v1/aktuator/{$led}/perintah", ['value' => $value])->assertUnprocessable();
        }
        foreach ([-1, 181, '90', 90.5, false, null] as $value) {
            $this->postJson("/api/v1/aktuator/{$servo}/perintah", ['value' => $value])->assertUnprocessable();
        }
        $this->assertDatabaseCount('actuator_commands', 0);
    }

    public function test_requested_and_reported_values_are_separate(): void
    {
        $id = $this->register(); $this->boot($id);
        $command = $this->command($id, 1);
        $this->assertDatabaseHas('actuators', ['id' => $id, 'requested_value' => 1, 'reported_value' => 0]);
        $this->getJson("/api/v1/aktuator/{$id}/perintah")->assertJsonPath('command.id', $command);
        $this->ack($id, $command, 1)->assertOk()->assertJsonPath('status', 'applied');
        $this->assertDatabaseHas('actuators', ['id' => $id, 'reported_value' => 1]);
        $this->assertDatabaseHas('actuator_state_events', ['command_id' => $command, 'value' => 1, 'reason' => 'command']);
        $event = ActuatorStateEvent::where('command_id', $command)->firstOrFail();
        $acknowledged = ActuatorCommand::findOrFail($command)->acknowledged_at;
        $this->assertLessThan(2, abs($event->created_at->diffInSeconds($acknowledged)));
        $this->getJson("/api/v1/aktuator/{$id}/perintah")->assertExactJson(['command' => null]);
    }

    public function test_servo_limits_are_applied_and_recorded(): void
    {
        $id = $this->register('pintu', 'servo'); $this->boot($id);
        foreach ([0, 90, 180] as $index => $value) {
            $command = $this->command($id, $value);
            $this->ack($id, $command, $value, $index + 2)->assertOk();
            $this->assertDatabaseHas('actuators', ['id' => $id, 'reported_value' => $value]);
        }
        $this->assertDatabaseCount('actuator_state_events', 4);
        $this->getJson("/api/v1/aktuator/{$id}/riwayat?limit=2")->assertJsonCount(2, 'events')->assertJsonCount(2, 'commands');
        $this->getJson("/api/v1/aktuator/{$id}/riwayat?limit=101")->assertUnprocessable();
    }

    public function test_wrong_actuator_value_boot_and_sequence_cannot_acknowledge(): void
    {
        $led = $this->register(); $this->boot($led);
        $servo = $this->register('pintu', 'servo'); $this->boot($servo);
        $command = $this->command($led, 1);
        $this->ack($servo, $command, 1)->assertNotFound();
        $this->ack($led, $command, 0)->assertUnprocessable();
        $this->ack($led, $command, 1, 2, '0000000000000000')->assertConflict();
        $this->ack($led, $command, 1, 1)->assertConflict();
        $this->assertDatabaseHas('actuator_commands', ['id' => $command, 'status' => 'pending']);
        $this->assertDatabaseHas('actuators', ['id' => $led, 'reported_value' => 0]);
    }

    public function test_new_command_supersedes_pending_command(): void
    {
        $id = $this->register(); $this->boot($id);
        $old = $this->command($id, 1); $new = $this->command($id, 0);
        $this->assertDatabaseHas('actuator_commands', ['id' => $old, 'status' => 'superseded']);
        $this->ack($id, $old, 1)->assertConflict();
        $this->getJson("/api/v1/aktuator/{$id}/perintah")->assertJsonPath('command.id', $new);
    }

    public function test_expired_command_is_not_returned_or_applied(): void
    {
        $id = $this->register(); $this->boot($id);
        $command = $this->command($id, 1);
        $this->travel(31)->seconds();
        $this->getJson("/api/v1/aktuator/{$id}/perintah")->assertExactJson(['command' => null]);
        $this->ack($id, $command, 1)->assertConflict();
        $this->assertDatabaseHas('actuator_commands', ['id' => $command, 'status' => 'expired']);
        $this->assertDatabaseHas('actuators', ['id' => $id, 'reported_value' => 0]);
    }

    public function test_duplicate_old_ack_does_not_rollback_new_state_or_duplicate_history(): void
    {
        $id = $this->register(); $this->boot($id);
        $on = $this->command($id, 1); $this->ack($id, $on, 1)->assertOk();
        $off = $this->command($id, 0); $this->ack($id, $off, 0, 3)->assertOk();
        $this->ack($id, $on, 1)->assertOk();
        $this->assertDatabaseHas('actuators', ['id' => $id, 'reported_value' => 0, 'report_sequence' => 3]);
        $this->assertDatabaseCount('actuator_state_events', 3);
    }

    public function test_restart_reports_safe_state_and_preserves_target_and_history(): void
    {
        $id = $this->register('pintu', 'servo'); $this->boot($id);
        $command = $this->command($id, 90); $this->ack($id, $command, 90)->assertOk();
        $pending = $this->command($id, 180);
        $this->boot($id, 'fedcba0987654321');
        $this->assertDatabaseHas('actuators', ['id' => $id, 'requested_value' => 180, 'reported_value' => 0]);
        $this->assertDatabaseHas('actuator_commands', ['id' => $command, 'status' => 'applied']);
        $this->assertDatabaseHas('actuator_commands', ['id' => $pending, 'status' => 'superseded']);
        $this->ack($id, $command, 90)->assertConflict();
        $this->assertDatabaseCount('actuator_state_events', 3);
    }

    public function test_duplicate_boot_and_heartbeat_do_not_duplicate_events(): void
    {
        $id = $this->register(); $this->boot($id);
        $command = $this->command($id, 1); $this->ack($id, $command, 1)->assertOk();
        $this->boot($id);
        $this->assertDatabaseHas('actuators', ['id' => $id, 'reported_value' => 1]);
        $this->postJson("/api/v1/aktuator/{$id}/status", ['value' => 1, 'boot_id' => self::BOOT,
            'sequence' => 3, 'reason' => 'heartbeat'])->assertOk();
        $this->assertDatabaseCount('actuator_state_events', 2);
        $this->postJson("/api/v1/aktuator/{$id}/status", ['value' => 0, 'boot_id' => self::BOOT,
            'sequence' => 2, 'reason' => 'heartbeat'])->assertConflict();
        $this->assertDatabaseHas('actuators', ['id' => $id, 'reported_value' => 1]);
    }

    public function test_unknown_boot_cannot_send_heartbeat_and_invalid_status_cannot_mutate_state(): void
    {
        $id = $this->register();
        $this->postJson("/api/v1/aktuator/{$id}/status", ['value' => 0, 'boot_id' => self::BOOT,
            'sequence' => 1, 'reason' => 'heartbeat'])->assertConflict();
        $this->postJson("/api/v1/aktuator/{$id}/status", ['value' => 9, 'boot_id' => self::BOOT,
            'sequence' => 1, 'reason' => 'boot'])->assertUnprocessable();
        $this->assertDatabaseCount('actuator_state_events', 0);
    }

    public function test_page_and_assets_are_available(): void
    {
        $this->get('/aktuator')->assertOk()->assertSee('Dilaporkan firmware')->assertSee('/actuators.js');
        $this->assertTrue(ActuatorCommand::query()->count() === 0);
        $this->assertTrue(ActuatorStateEvent::query()->count() === 0);
        $this->assertTrue(Actuator::query()->count() === 0);
    }
}
