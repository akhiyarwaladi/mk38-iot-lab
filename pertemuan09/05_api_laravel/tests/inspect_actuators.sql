SELECT id, device_id, name, kind,
       requested_value, reported_value, boot_id, reported_at
FROM actuators
WHERE device_id = 'esp32-aktuator-01';

SELECT c.id, a.name, c.value, c.status, c.acknowledged_at
FROM actuator_commands c
JOIN actuators a ON a.id = c.actuator_id
WHERE a.device_id = 'esp32-aktuator-01'
ORDER BY c.id DESC;

SELECT e.id, a.name, e.command_id, e.value,
       e.reason, e.boot_id, e.sequence, e.created_at
FROM actuator_state_events e
JOIN actuators a ON a.id = e.actuator_id
WHERE a.device_id = 'esp32-aktuator-01'
ORDER BY e.id DESC;
