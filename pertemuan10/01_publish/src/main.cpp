#include <Arduino.h>
#include <WiFi.h>
#include <MQTT.h>
#include "config.h"

WiFiClient jaringan;
MQTTClient mqtt(256);
String topikPesan;
String idKlien;
unsigned long terakhirCoba = 0;
unsigned long terakhirKirim = 0;

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  topikPesan = String(TOPIC_ROOT) + "/pesan";
  idKlien = String(TOPIC_ROOT) + "-" + WiFi.macAddress();
  mqtt.begin(MQTT_HOST, MQTT_PORT, jaringan);
  mqtt.setOptions(15, true, 1500);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) { delay(10); return; }
  if (!mqtt.connected()) {
    if (millis() - terakhirCoba < 5000) { delay(10); return; }
    terakhirCoba = millis();
    if (mqtt.connect(idKlien.c_str())) {
      Serial.println("MQTT tersambung.");
    } else {
      Serial.printf("MQTT gagal, kode: %d\n", mqtt.lastError());
    }
    return;
  }
  mqtt.loop();
  if (millis() - terakhirKirim >= 5000) {
    terakhirKirim = millis();
    bool berhasil = mqtt.publish(topikPesan, "Halo dari ESP32", false, 0);
    Serial.println(berhasil ? "Pesan dikirim." : "Pengiriman gagal.");
  }
  delay(2);
}
