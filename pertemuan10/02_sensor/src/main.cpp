#include <Arduino.h>
#include <WiFi.h>
#include <MQTT.h>
#include <DHTesp.h>
#include "config.h"

WiFiClient jaringan;
MQTTClient mqtt(256);
DHTesp dht;
String topikSensor;
String idKlien;
unsigned long terakhirCoba = 0;
unsigned long terakhirKirim = 0;

void setup() {
  Serial.begin(115200);
  dht.setup(15, DHTesp::DHT22);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  topikSensor = String(TOPIC_ROOT) + "/sensor";
  idKlien = String(TOPIC_ROOT) + "-" + WiFi.macAddress();
  mqtt.begin(MQTT_HOST, MQTT_PORT, jaringan);
  mqtt.setOptions(15, true, 1500);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) { delay(10); return; }
  if (!mqtt.connected()) {
    if (millis() - terakhirCoba < 5000) { delay(10); return; }
    terakhirCoba = millis();
    if (mqtt.connect(idKlien.c_str())) Serial.println("MQTT tersambung.");
    else Serial.printf("MQTT gagal, kode: %d\n", mqtt.lastError());
    return;
  }
  mqtt.loop();
  if (millis() - terakhirKirim >= 5000) {
    terakhirKirim = millis();
    TempAndHumidity data = dht.getTempAndHumidity();
    if (isnan(data.temperature) || isnan(data.humidity)) {
      Serial.println("Sensor tidak valid; kiriman dilewati.");
      return;
    }
    char muatan[96];
    snprintf(muatan, sizeof(muatan),
             "{\"suhu\":%.1f,\"kelembapan\":%.1f}",
             data.temperature, data.humidity);
    bool berhasil = mqtt.publish(topikSensor, muatan, false, 0);
    Serial.println(berhasil ? muatan : "Pengiriman gagal.");
  }
  delay(2);
}
