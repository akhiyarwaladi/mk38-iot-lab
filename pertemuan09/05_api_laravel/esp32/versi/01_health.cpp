#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include "config.h"

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6);
  unsigned long mulai = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - mulai < 15000) {
    delay(250);
  }
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi belum tersambung.");
    delay(5000);
    return;
  }
  WiFiClient client;
  HTTPClient http;
  http.setConnectTimeout(3000);
  http.setTimeout(3000);
  http.begin(client, String(API_BASE) + "/api/v1/health");
  int status = http.GET();
  Serial.printf("GET /api/v1/health -> %d\n", status);
  Serial.println(status > 0 ? http.getString() : HTTPClient::errorToString(status));
  http.end();
  delay(5000);
}

