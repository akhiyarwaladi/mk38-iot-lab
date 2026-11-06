#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <DHTesp.h>
#include "config.h"

DHTesp dht;

void setup() {
  Serial.begin(115200);
  dht.setup(15, DHTesp::DHT22);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6);
  unsigned long mulai = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - mulai < 15000) {
    delay(250);
  }
  delay(2000);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi belum tersambung; lewati kiriman.");
    delay(5000);
    return;
  }
  TempAndHumidity data = dht.getTempAndHumidity();
  if (!isfinite(data.temperature) || !isfinite(data.humidity)) {
    Serial.println("Sensor belum siap; lewati kiriman.");
    delay(5000);
    return;
  }
  String body = String("{\"device_id\":\"") + DEVICE_ID +
      "\",\"suhu\":" + String(data.temperature, 1) +
      ",\"kelembapan\":" + String(data.humidity, 1) + "}";
  WiFiClient client;
  HTTPClient http;
  http.setConnectTimeout(3000);
  http.setTimeout(3000);
  if (!http.begin(client, String(API_BASE) + "/api/v1/sensor")) {
    Serial.println("Gagal menyiapkan HTTP client.");
    delay(5000);
    return;
  }
  http.addHeader("Content-Type", "application/json");
  http.addHeader("Accept", "application/json");
  int status = http.POST(body);
  Serial.printf("POST sensor -> %d\n", status);
  if (status > 0) {
    Serial.println(http.getString());
    if (status == 201) Serial.println("Periksa id ini melalui GET dan database.");
  } else {
    Serial.println(HTTPClient::errorToString(status));
  }
  http.end();
  delay(5000);
}
