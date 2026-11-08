CREATE DATABASE IF NOT EXISTS mk38_sensor
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'mk38_sensor'@'localhost'
  IDENTIFIED BY 'ganti_password_praktikum';
GRANT ALL PRIVILEGES ON mk38_sensor.*
  TO 'mk38_sensor'@'localhost';
