USE mk38_sensor;
SELECT id, device_id, suhu, kelembapan, created_at
FROM sensors ORDER BY id DESC LIMIT 5;
