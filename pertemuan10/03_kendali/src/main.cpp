#include <Arduino.h>
#include <WiFi.h>
#include <MQTT.h>
#include <DHTesp.h>
#include "config.h"

WiFiClient jaringan;
MQTTClient mqtt(256);
DHTesp dht;
const int LED_PIN = 23;
String topikSensor, topikPerintah, topikKeadaan, idKlien;
bool ledMenyala = false;
bool keadaanPerluDikirim = true;
unsigned long terakhirCoba = 0;
unsigned long terakhirKirim = 0;

void terimaPesan(String& topik, String& muatan) {
  if (topik != topikPerintah) return;
  if (muatan != "on" && muatan != "off") {
    Serial.println("Perintah ditolak: gunakan on atau off.");
    return;
  }
  ledMenyala = muatan == "on";
  digitalWrite(LED_PIN, ledMenyala ? HIGH : LOW);
  keadaanPerluDikirim = true;
  Serial.printf("LED=%s PIN=%d\n", ledMenyala ? "on" : "off",
                digitalRead(LED_PIN));
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  dht.setup(15, DHTesp::DHT22);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  topikSensor = String(TOPIC_ROOT) + "/sensor";
  topikPerintah = String(TOPIC_ROOT) + "/led/set";
  topikKeadaan = String(TOPIC_ROOT) + "/led/state";
  idKlien = String(TOPIC_ROOT) + "-" + WiFi.macAddress();
  mqtt.begin(MQTT_HOST, MQTT_PORT, jaringan);
  mqtt.setOptions(15, true, 1500);
  mqtt.onMessage(terimaPesan);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) { delay(10); return; }
  if (!mqtt.connected()) {
    if (millis() - terakhirCoba < 5000) { delay(10); return; }
    terakhirCoba = millis();
    if (mqtt.connect(idKlien.c_str())) {
      if (!mqtt.subscribe(topikPerintah, 1)) {
        Serial.println("Subscribe gagal; sambungan akan dicoba ulang.");
        mqtt.disconnect();
        return;
      }
      keadaanPerluDikirim = true;
      Serial.println("MQTT tersambung; langganan perintah aktif.");
    } else Serial.printf("MQTT gagal, kode: %d\n", mqtt.lastError());
    return;
  }
  mqtt.loop();
  if (keadaanPerluDikirim && mqtt.connected()) {
    bool keadaanTerkirim = ledMenyala;
    if (mqtt.publish(topikKeadaan, keadaanTerkirim ? "on" : "off", true, 1)
        && keadaanTerkirim == ledMenyala)
      keadaanPerluDikirim = false;
  }
  if (millis() - terakhirKirim >= 5000) {
    terakhirKirim = millis();
    TempAndHumidity data = dht.getTempAndHumidity();
    if (isnan(data.temperature) || isnan(data.humidity)) {
      Serial.println("Sensor tidak valid; kiriman dilewati.");
      return;
    }
    char muatan[96];
    snprintf(muatan, sizeof(muatan),
             "{\"suhu\":%.1f,\"kelembapan\":%.1f,\"led\":%s}",
             data.temperature, data.humidity, ledMenyala ? "true" : "false");
    bool berhasil = mqtt.publish(topikSensor, muatan, false, 0);
    Serial.println(berhasil ? muatan : "Pengiriman gagal.");
  }
  delay(2);
}
