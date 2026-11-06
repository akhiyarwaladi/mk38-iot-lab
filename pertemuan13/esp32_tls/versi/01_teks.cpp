#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <MQTT.h>
#include <time.h>
#include "broker_ca.h"
#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#endif

WiFiClientSecure transport;
MQTTClient mqtt(512);
String clientId, topic;
unsigned long terakhirSambung = 0, terakhirKirim = 0;

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org", "time.google.com");
  transport.setCACert(BROKER_CA);
  transport.setHandshakeTimeout(15);
  mqtt.begin(MQTT_HOST, MQTT_PORT, transport);
  mqtt.setOptions(30, true, 2000);
  clientId = String(TOPIC_ROOT) + "-" + WiFi.macAddress();
  topic = String(TOPIC_ROOT) + "/pesan";
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
    if (mqtt.publish(topic, "Halo melalui TLS", false, 0)) Serial.println("Teks dikirim");
  }
  delay(2);
}
