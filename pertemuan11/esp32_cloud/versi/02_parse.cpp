#include <Arduino.h>
#include <WiFi.h>
#include <time.h>
#include "config.h"
#include "cloud.h"

unsigned long terakhir = 0;

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org", "time.google.com");
}

void loop() {
  if (WiFi.status() != WL_CONNECTED || time(nullptr) < 1700000000) {
    delay(10);
    return;
  }
  if (millis() - terakhir < 20000) return;
  terakhir = millis();
  CloudResult hasil = kirimCloud(0, 0, false, true, "");
  Serial.printf("http=%d read_ok=%d public_entry_id=%ld\n",
                hasil.http, hasil.readOk, hasil.publicEntryId);
}
