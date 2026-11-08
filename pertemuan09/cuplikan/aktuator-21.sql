SELECT c.id, a.name, c.value, c.status, c.acknowledged_at
FROM actuator_commands c
JOIN actuators a ON a.id = c.actuator_id
WHERE a.device_id = 'esp32-aktuator-01'
ORDER BY c.id DESC;
