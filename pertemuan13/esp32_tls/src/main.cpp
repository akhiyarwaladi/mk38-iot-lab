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
String sensorTopic, commandTopic, stateTopic, clientId;
bool ledOn = false, pendingState = true;
unsigned long lastConnect = 0, lastSensor = 0, lastClockLog = 0;

void onMessage(String& topic, String& payload) {
  if (topic != commandTopic) return;
  if (payload != "on" && payload != "off") {
    Serial.println("Perintah ditolak: gunakan on atau off.");
    return;
  }
  ledOn = payload == "on";
  digitalWrite(23, ledOn ? HIGH : LOW);
  pendingState = true;
  Serial.printf("LED=%s PIN=%d\n", ledOn ? "on" : "off", digitalRead(23));
}

void setup() {
  Serial.begin(115200);
  pinMode(23, OUTPUT);
  digitalWrite(23, LOW);
  dht.setup(15, DHTesp::DHT22);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org", "time.google.com");
  transport.setCACert(BROKER_CA);
  transport.setHandshakeTimeout(15);
  transport.setTimeout(10000);
  mqtt.begin(MQTT_HOST, MQTT_PORT, transport);
  mqtt.setOptions(30, true, 2000);
  mqtt.onMessage(onMessage);
  sensorTopic = String(TOPIC_ROOT) + "/sensor";
  commandTopic = String(TOPIC_ROOT) + "/led/set";
  stateTopic = String(TOPIC_ROOT) + "/led/state";
  clientId = String(TOPIC_ROOT) + "-" + WiFi.macAddress();
  Serial.printf("Firmware=%s TLS host=%s port=%d\n",
                FIRMWARE_VERSION, MQTT_HOST, MQTT_PORT);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) { delay(10); return; }
  if (time(nullptr) < 1700000000) {
    if (millis() - lastClockLog > 5000) {
      lastClockLog = millis();
      Serial.println("Menunggu waktu NTP untuk validasi sertifikat.");
    }
    delay(10); return;
  }
  if (!mqtt.connected()) {
    if (millis() - lastConnect < 5000) { delay(2); return; }
    lastConnect = millis();
    if (mqtt.connect(clientId.c_str(), MQTT_USER, MQTT_PASSWORD)
        && mqtt.subscribe(commandTopic, 1)) {
      pendingState = true;
      Serial.println("MQTTS connected; command subscription aktif.");
    } else {
      Serial.printf("MQTTS gagal: error=%d returnCode=%d\n",
                    mqtt.lastError(), mqtt.returnCode());
      mqtt.disconnect();
    }
    return;
  }
  mqtt.loop();
  if (pendingState && mqtt.connected()) {
    bool snapshot = ledOn;
    if (mqtt.publish(stateTopic, snapshot ? "on" : "off", true, 1)
        && ledOn == snapshot) pendingState = false;
  }
  if (millis() - lastSensor >= 5000) {
    lastSensor = millis();
    TempAndHumidity data = dht.getTempAndHumidity();
    if (!isnan(data.temperature) && !isnan(data.humidity)) {
      JsonDocument sample;
      sample["suhu"] = data.temperature;
      sample["kelembapan"] = data.humidity;
      sample["led"] = ledOn;
      sample["firmware"] = FIRMWARE_VERSION;
      String payload;
      serializeJson(sample, payload);
      if (mqtt.publish(sensorTopic, payload, false, 0)) Serial.println(payload);
    } else Serial.println("Sensor tidak valid; publish dilewati.");
  }
  delay(2);
}
