#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <time.h>
#include "root_ca.h"

unsigned long terakhir = 0;

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin("Wokwi-GUEST", "");
  configTime(0, 0, "pool.ntp.org", "time.google.com");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED || time(nullptr) < 1700000000) {
    delay(10);
    return;
  }
  if (millis() - terakhir < 20000) return;
  terakhir = millis();
  WiFiClientSecure tls;
  tls.setCACert(ROOT_CA);
  HTTPClient http;
  http.setConnectTimeout(15000);
  http.setTimeout(10000);
  if (http.begin(tls, "https://api.thingspeak.com/channels/9/feeds/last.json")) {
    int status = http.GET();
    Serial.printf("HTTPS GET status=%d\n", status);
    if (status > 0) Serial.println(http.getString());
    else Serial.println(HTTPClient::errorToString(status));
    http.end();
  }
}
