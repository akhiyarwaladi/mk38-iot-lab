#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <DHTesp.h>
#include <ArduinoJson.h>
#include "config.h"

const int LED_PIN = 23;
DHTesp dht;
unsigned long terakhirSensor = 0;
unsigned long terakhirPerintah = 0;

int requestApi(const String& path, const String& body, String& reply) {
  WiFiClient client;
  HTTPClient http;
  http.setConnectTimeout(2000);
  http.setTimeout(3000);
  if (!http.begin(client, String(API_BASE) + path)) return -1;
  http.addHeader("Accept", "application/json");
  http.addHeader("Content-Type", "application/json");
  int status = body.isEmpty() ? http.GET() : http.POST(body);
  reply = status > 0 ? http.getString() : HTTPClient::errorToString(status);
  http.end();
  return status;
}

void kirimSensor() {
  TempAndHumidity data = dht.getTempAndHumidity();
  if (!isfinite(data.temperature) || !isfinite(data.humidity)) return;
  String body = String("{\"device_id\":\"") + DEVICE_ID +
      "\",\"suhu\":" + String(data.temperature, 1) +
      ",\"kelembapan\":" + String(data.humidity, 1) + "}";
  String reply;
  int status = requestApi("/api/v1/sensor", body, reply);
  Serial.printf("POST sensor -> %d\n", status);
  Serial.println(reply);
}

void laporLed() {
  String body = String("{\"led\":") + (digitalRead(LED_PIN) == HIGH ? "true}" : "false}");
  String reply;
  int status = requestApi(String("/api/v1/perangkat/") + DEVICE_ID + "/status", body, reply);
  if (status != 200) Serial.printf("Laporan LED gagal: %d\n", status);
}

void periksaPerintah() {
  String path = String("/api/v1/perangkat/") + DEVICE_ID;
  String reply;
  if (requestApi(path + "/perintah", "", reply) != 200) return;
  JsonDocument document;
  if (deserializeJson(document, reply) || document["command"].isNull()) return;
  JsonObject command = document["command"].as<JsonObject>();
  if (!command["id"].is<unsigned long>() || !command["led"].is<bool>()) {
    Serial.println("Perintah tidak valid; LED tidak diubah.");
    return;
  }
  digitalWrite(LED_PIN, command["led"].as<bool>() ? HIGH : LOW);
  bool applied = digitalRead(LED_PIN) == HIGH;
  String body = String("{\"command_id\":") + command["id"].as<unsigned long>() +
      ",\"led\":" + (applied ? "true}" : "false}");
  int status = requestApi(path + "/konfirmasi", body, reply);
  Serial.printf("LED %s; konfirmasi perintah %lu -> %d\n",
      applied ? "on" : "off", command["id"].as<unsigned long>(), status);
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  dht.setup(15, DHTesp::DHT22);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6);
  unsigned long mulai = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - mulai < 15000) delay(250);
  delay(2000);
  if (WiFi.status() == WL_CONNECTED) { kirimSensor(); laporLed(); }
  terakhirSensor = millis();
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) { delay(100); return; }
  if (millis() - terakhirPerintah >= 1000) {
    terakhirPerintah = millis();
    periksaPerintah();
  }
  if (millis() - terakhirSensor >= 5000) {
    terakhirSensor = millis();
    kirimSensor();
    laporLed();
  }
  delay(10);
}
