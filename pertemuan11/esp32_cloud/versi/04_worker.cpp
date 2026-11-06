#include <Arduino.h>
#include <WiFi.h>
#include <time.h>
#include "config.h"
#include "cloud.h"

unsigned long terakhir = 0, detikTerakhir = 0;
bool siap = false;

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  configTime(0, 0, "pool.ntp.org", "time.google.com");
  siap = mulaiCloudWorker(REST_INTERVAL);
  Serial.println(siap ? "Worker siap" : "Worker gagal dibuat");
}

void loop() {
  if (millis() - detikTerakhir >= 1000) {
    detikTerakhir = millis();
    Serial.println("Loop tetap berjalan");
  }
  if (siap && WiFi.status() == WL_CONNECTED && time(nullptr) >= 1700000000
      && millis() - terakhir >= REST_INTERVAL) {
    terakhir = millis();
    antreCloud(0, 0, false, true, "");
    Serial.println("Baca publik masuk antrean");
  }
  CloudReport report;
  if (ambilHasilCloud(report)) {
    Serial.printf("http=%d read_ok=%d public_entry_id=%ld\n",
                  report.result.http, report.result.readOk, report.result.publicEntryId);
  }
  delay(2);
}
