#include <Arduino.h>
#include <WiFi.h>
#include <MQTT.h>
#include <DHTesp.h>
#include <ArduinoJson.h>
#include <time.h>
#include "config.h"
#include "cloud.h"
#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#endif

WiFiClient jaringan;
MQTTClient mqtt(512);
DHTesp dht;
const int LED_PIN = 23;
String sensorTopic, commandTopic, stateTopic, cloudTopic, clientId;
String pendingCloud;
bool ledOn = false, pendingState = true;
bool cloudReady = false;
unsigned long lastConnect = 0, lastSensor = 0, lastRest = 0;

void onMessage(String& topic, String& payload) {
  if (topic != commandTopic) return;
  if (payload != "on" && payload != "off") {
    Serial.println("Perintah ditolak: gunakan on atau off.");
    return;
  }
  ledOn = payload == "on";
  digitalWrite(LED_PIN, ledOn ? HIGH : LOW);
  pendingState = true;
  Serial.printf("LED=%s PIN=%d\n", ledOn ? "on" : "off", digitalRead(LED_PIN));
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  dht.setup(15, DHTesp::DHT22);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org", "time.google.com");
  sensorTopic = String(TOPIC_ROOT) + "/sensor";
  commandTopic = String(TOPIC_ROOT) + "/led/set";
  stateTopic = String(TOPIC_ROOT) + "/led/state";
  cloudTopic = String(TOPIC_ROOT) + "/cloud/status";
  clientId = String(TOPIC_ROOT) + "-" + WiFi.macAddress();
  mqtt.begin(MQTT_HOST, MQTT_PORT, jaringan);
  mqtt.setOptions(30, true, 1500);
  mqtt.onMessage(onMessage);
  cloudReady = mulaiCloudWorker(REST_INTERVAL);
  if (!cloudReady) Serial.println("Task REST gagal dibuat; periksa RAM.");
  Serial.println(MODE_BACA_PUBLIK ? "MODE=BACA_PUBLIK; bukan penyimpanan ThingSpeak."
                          : "MODE=THINGSPEAK");
}

void jagaMQTT() {
  if (!mqtt.connected()) {
    if (millis() - lastConnect < 5000) return;
    lastConnect = millis();
    if (mqtt.connect(clientId.c_str()) && mqtt.subscribe(commandTopic, 1)) {
      pendingState = true;
      Serial.println("MQTT connected; command subscription aktif.");
    } else mqtt.disconnect();
    return;
  }
  mqtt.loop();
  if (pendingState && mqtt.connected()) {
    bool snapshot = ledOn;
    if (mqtt.publish(stateTopic, snapshot ? "on" : "off", true, 1)
        && snapshot == ledOn) pendingState = false;
  }
  if (pendingCloud.length() && mqtt.connected()) {
    if (mqtt.publish(cloudTopic, pendingCloud, false, 1)) pendingCloud = "";
  }
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) { delay(10); return; }
  jagaMQTT();
  CloudReport report;
  if (ambilHasilCloud(report)) {
    JsonDocument status;
    status["mode"] = report.modeBacaPublik ? "read_public" : "thingspeak";
    status["http"] = report.result.http;
    status["entry_id"] = report.result.entryId;
    status["tersimpan"] = !report.modeBacaPublik && report.result.entryId > 0;
    status["read_ok"] = report.result.readOk;
    status["public_entry_id"] = report.result.publicEntryId;
    pendingCloud = "";
    serializeJson(status, pendingCloud);
    Serial.println(pendingCloud);
  }
  if (millis() - lastSensor >= MQTT_INTERVAL) {
    lastSensor = millis();
    TempAndHumidity data = dht.getTempAndHumidity();
    if (!isnan(data.temperature) && !isnan(data.humidity)) {
      JsonDocument sensor;
      sensor["suhu"] = data.temperature;
      sensor["kelembapan"] = data.humidity;
      sensor["led"] = ledOn;
      String payload;
      serializeJson(sensor, payload);
      if (mqtt.connected()) mqtt.publish(sensorTopic, payload, false, 0);
      Serial.println(payload);
    } else Serial.println("Sensor tidak valid; publish dilewati.");
  }
  if (millis() - lastRest >= REST_INTERVAL) {
    lastRest = millis();
    if (!cloudReady) return;
    if (!MODE_BACA_PUBLIK && String(THINGSPEAK_WRITE_KEY) == "ISI_WRITE_API_KEY") {
      Serial.println("REST belum aktif: isi secrets.h dan build ulang.");
      return;
    }
    if (time(nullptr) < 1700000000) {
      Serial.println("REST menunggu waktu NTP untuk TLS.");
      return;
    }
    TempAndHumidity data = dht.getTempAndHumidity();
    if (isnan(data.temperature) || isnan(data.humidity)) return;
    if (antreCloud(data.temperature, data.humidity, ledOn,
                   MODE_BACA_PUBLIK, THINGSPEAK_WRITE_KEY))
      Serial.println("REST masuk antrean; MQTT tetap dilayani.");
  }
  delay(2);
}
