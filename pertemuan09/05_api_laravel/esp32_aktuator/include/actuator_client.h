#pragma once
#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include "config.h"

struct Aktuator {
  Aktuator(const char* namaAwal, const char* jenisAwal) : nama(namaAwal), jenis(jenisAwal) {}
  const char* nama;
  const char* jenis;
  int id = 0;
  int nilai = 0;
  uint32_t urutan = 0;
  bool siap = false;
  String konfirmasi;
};

String bootId;

int api(const String& path, const String& body, String& reply) {
  WiFiClient client;
  HTTPClient http;
  http.setConnectTimeout(2000);
  http.setTimeout(3000);
  if (!http.begin(client, String(API_BASE) + "/api/v1/aktuator" + path)) return -1;
  http.addHeader("Accept", "application/json");
  http.addHeader("Content-Type", "application/json");
  int code = body.isEmpty() ? http.GET() : http.POST(body);
  reply = code > 0 ? http.getString() : HTTPClient::errorToString(code);
  http.end();
  return code;
}

String laporan(Aktuator& a, const char* alasan) {
  JsonDocument doc;
  doc["value"] = a.nilai;
  doc["boot_id"] = bootId;
  doc["sequence"] = ++a.urutan;
  doc["reason"] = alasan;
  String body;
  serializeJson(doc, body);
  return body;
}

bool daftarkan(Aktuator& a) {
  JsonDocument doc;
  doc["device_id"] = DEVICE_ID;
  doc["name"] = a.nama;
  doc["kind"] = a.jenis;
  String body, reply;
  serializeJson(doc, body);
  int code = api("", body, reply);
  if (code != 200 && code != 201) return false;
  if (deserializeJson(doc, reply) || !doc["id"].is<int>()) return false;
  a.id = doc["id"];
  code = api("/" + String(a.id) + "/status", laporan(a, "boot"), reply);
  Serial.printf("BOOT %s id=%d nilai=%d -> %d\n", a.nama, a.id, a.nilai, code);
  a.siap = code == 200;
  return a.siap;
}

bool kirimKonfirmasi(Aktuator& a) {
  if (a.konfirmasi.isEmpty()) return true;
  String reply;
  int code = api("/" + String(a.id) + "/konfirmasi", a.konfirmasi, reply);
  Serial.printf("ACK %s nilai=%d -> %d\n", a.nama, a.nilai, code);
  if (code == 200 || code == 409 || code == 404 || code == 422) a.konfirmasi = "";
  return a.konfirmasi.isEmpty();
}

void periksa(Aktuator& a, void (*terapkan)(int)) {
  if (!a.siap) { daftarkan(a); return; }
  if (!kirimKonfirmasi(a)) return;
  String reply;
  if (api("/" + String(a.id) + "/perintah", "", reply) != 200) return;
  JsonDocument doc;
  if (deserializeJson(doc, reply) || doc["command"].isNull()) return;
  JsonObject command = doc["command"];
  if (!command["id"].is<int>() || !command["value"].is<int>()) return;
  int nilai = command["value"];
  int maks = String(a.jenis) == "led" ? 1 : 180;
  if (nilai < 0 || nilai > maks) return;
  int commandId = command["id"];
  terapkan(nilai);
  a.nilai = String(a.jenis) == "led" ? digitalRead(23) : nilai;
  JsonDocument ack;
  ack["command_id"] = commandId;
  ack["value"] = a.nilai;
  ack["boot_id"] = bootId;
  ack["sequence"] = ++a.urutan;
  serializeJson(ack, a.konfirmasi);
  Serial.printf("APPLY %s command=%d nilai=%d\n", a.nama, commandId, a.nilai);
  kirimKonfirmasi(a);
}

void heartbeat(Aktuator& a) {
  if (!a.siap || !a.konfirmasi.isEmpty()) return;
  String reply;
  int code = api("/" + String(a.id) + "/status", laporan(a, "heartbeat"), reply);
  if (code != 200) Serial.printf("Laporan %s -> %d\n", a.nama, code);
}

void mulaiWifi() {
  char id[17];
  snprintf(id, sizeof(id), "%08lx%08lx", (unsigned long)esp_random(), (unsigned long)esp_random());
  bootId = id;
  Serial.printf("Sesi %s\n", bootId.c_str());
  WiFi.begin("Wokwi-GUEST", "", 6);
}

bool wifiSiap() {
  static unsigned long terakhir = 0;
  if (WiFi.status() == WL_CONNECTED) return true;
  if (millis() - terakhir >= 15000) { terakhir = millis(); WiFi.reconnect(); }
  return false;
}
