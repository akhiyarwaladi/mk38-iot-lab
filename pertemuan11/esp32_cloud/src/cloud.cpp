#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <limits.h>
#include "cloud.h"
#include "thingspeak_ca.h"

long bacaEntryId(int status, String respons) {
  if (status != 200) return 0;
  respons.trim();
  if (respons.length() == 0) return 0;
  long value = 0;
  for (unsigned int i = 0; i < respons.length(); i++) {
    char digit = respons[i];
    if (digit < '0' || digit > '9') return 0;
    int n = digit - '0';
    if (value > (LONG_MAX - n) / 10) return 0;
    value = value * 10 + n;
  }
  return value;
}

CloudResult kirimCloud(float suhu, float kelembapan, bool led,
                      bool modeBacaPublik, const char* writeKey) {
  CloudResult result;
  WiFiClientSecure tls;
  tls.setCACert(THINGSPEAK_CA);
  tls.setHandshakeTimeout(30);
  HTTPClient http;
  http.setConnectTimeout(15000);
  http.setTimeout(10000);
  http.setFollowRedirects(HTTPC_DISABLE_FOLLOW_REDIRECTS);
  const char* url = modeBacaPublik ? "https://api.thingspeak.com/channels/9/feeds/last.json"
                             : "https://api.thingspeak.com/update";
  if (!http.begin(tls, url)) { result.http = -1; return result; }
  JsonDocument request;
  if (!modeBacaPublik) request["api_key"] = writeKey;
  request["field1"] = suhu;
  request["field2"] = kelembapan;
  request["field3"] = led ? 1 : 0;
  String payload;
  serializeJson(request, payload);
  http.addHeader("Content-Type", "application/json");
  result.http = modeBacaPublik ? http.GET() : http.POST(payload);
  String respons = result.http > 0 ? http.getString() : "";
  http.end();
  if (modeBacaPublik && result.http == 200) {
    JsonDocument feed;
    if (!deserializeJson(feed, respons)) {
      result.readOk = feed["entry_id"].is<long>() &&
          feed["entry_id"].as<long>() > 0 && feed["created_at"].is<const char*>();
      if (result.readOk) result.publicEntryId = feed["entry_id"].as<long>();
    }
  } else if (!modeBacaPublik) result.entryId = bacaEntryId(result.http, respons);
  return result;
}
