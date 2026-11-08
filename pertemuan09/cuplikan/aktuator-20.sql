SELECT id, device_id, name, kind,
       requested_value, reported_value, boot_id, reported_at
FROM actuators
WHERE device_id = 'esp32-aktuator-01';
