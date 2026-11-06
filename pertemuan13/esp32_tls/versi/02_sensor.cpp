#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <MQTT.h>
#include <DHTesp.h>
#include <ArduinoJson.h>
#include <time.h>
#include "broker_ca.h"
#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#endif

WiFiClientSecure transport;
MQTTClient mqtt(768);
DHTesp dht;
String clientId, topic;
unsigned long terakhirSambung = 0, terakhirKirim = 0;

void setup() {
  Serial.begin(115200);
  dht.setup(15, DHTesp::DHT22);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org", "time.google.com");
  transport.setCACert(BROKER_CA);
  transport.setHandshakeTimeout(15);
  mqtt.begin(MQTT_HOST, MQTT_PORT, transport);
  mqtt.setOptions(30, true, 2000);
  clientId = String(TOPIC_ROOT) + "-" + WiFi.macAddress();
  topic = String(TOPIC_ROOT) + "/sensor";
}

void loop() {
  if (WiFi.status() != WL_CONNECTED || time(nullptr) < 1700000000) {
    delay(10);
    return;
  }
  if (!mqtt.connected()) {
    if (millis() - terakhirSambung < 5000) return;
    terakhirSambung = millis();
    bool ok = mqtt.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD);
    Serial.printf("MQTTS connected=%d error=%d\n", ok, mqtt.lastError());
    return;
  }
  mqtt.loop();
  if (millis() - terakhirKirim >= 5000) {
    terakhirKirim = millis();
    TempAndHumidity data = dht.getTempAndHumidity();
    if (isnan(data.temperature) || isnan(data.humidity)) return;
    JsonDocument sample;
    sample["suhu"] = data.temperature;
    sample["kelembapan"] = data.humidity;
    sample["led"] = false;
    sample["firmware"] = FIRMWARE_VERSION;
    String payload;
    serializeJson(sample, payload);
    if (mqtt.publish(topic, payload, false, 0)) Serial.println(payload);
  }
  delay(2);
}
