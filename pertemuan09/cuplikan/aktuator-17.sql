SELECT e.id, a.name, e.command_id, e.value,
       e.reason, e.boot_id, e.sequence, e.created_at
FROM actuator_state_events e
JOIN actuators a ON a.id = e.actuator_id
WHERE a.device_id = 'esp32-aktuator-01'
ORDER BY e.id DESC;
