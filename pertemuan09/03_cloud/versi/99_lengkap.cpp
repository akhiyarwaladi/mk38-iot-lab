#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <DHTesp.h>
#include <time.h>
#include "root_ca.h"

#if __has_include("secrets.h")
#include "secrets.h"
#else
#include "secrets.example.h"
#endif

DHTesp dht;
const char* SSID = "Wokwi-GUEST";
const char* PASSWORD = "";

void setup() {
  Serial.begin(115200);
  dht.setup(15, DHTesp::DHT22);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(SSID, PASSWORD);
  unsigned long mulai = millis();
  while (WiFi.status() != WL_CONNECTED &&
         millis() - mulai < 15000) {
    delay(250);
  }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi belum tersambung; kiriman akan dilewati.");
  }
  configTime(0, 0, "pool.ntp.org", "time.google.com");
  mulai = millis();
  while (time(nullptr) < 1700000000 && millis() - mulai < 20000) {
    delay(250);
  }
  delay(2000);
}

void loop() {
  if (String(THINGSPEAK_WRITE_KEY) == "ISI_WRITE_API_KEY") {
    Serial.println("Isi include/secrets.h dengan Write API Key channel.");
    delay(20000);
    return;
  }
  if (WiFi.status() != WL_CONNECTED || time(nullptr) < 1700000000) {
    Serial.println("Lewati kiriman: Wi-Fi atau waktu TLS belum siap.");
    delay(20000);
    return;
  }
  TempAndHumidity data = dht.getTempAndHumidity();
  if (isnan(data.temperature) || isnan(data.humidity)) {
    Serial.println("Lewati kiriman: data sensor tidak valid.");
    delay(20000);
    return;
  }

  WiFiClientSecure tls;
  tls.setCACert(ROOT_CA);
  HTTPClient http;
  http.setConnectTimeout(5000);
  http.setTimeout(5000);
  if (!http.begin(tls, "https://api.thingspeak.com/update")) {
    Serial.println("Gagal menyiapkan HTTP client.");
    delay(20000);
    return;
  }
  http.addHeader("Content-Type", "application/json");
  String body = String("{\"api_key\":\"") + THINGSPEAK_WRITE_KEY +
      "\",\"field1\":" + String(data.temperature, 1) +
      ",\"field2\":" + String(data.humidity, 1) + "}";

  int status = http.POST(body);
  String respons = status > 0 ? http.getString() : "";
  Serial.printf("HTTP status: %d\n", status);
  if (status == 200 && respons.toInt() > 0) {
    Serial.printf("Tersimpan. Entry ID: %ld\n", respons.toInt());
  } else {
    Serial.println("Belum tersimpan. Periksa key, jaringan, dan interval.");
    Serial.println(status > 0 ? respons : HTTPClient::errorToString(status));
  }
  http.end();
  delay(20000);
}
