#pragma once
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";
const char* MQTT_HOST = "broker.hivemq.com";
const int MQTT_PORT = 1883;
const char* TOPIC_ROOT = "unja/mk38/p11/ganti-nim-anda";
// true: diagnosis HTTPS tanpa akun; false: simpan ke ThingSpeak.
bool MODE_BACA_PUBLIK = true;
const unsigned long MQTT_INTERVAL = 5000;
const unsigned long REST_INTERVAL = 20000;
