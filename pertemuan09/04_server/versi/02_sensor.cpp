#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <DHTesp.h>

WebServer server(80);
DHTesp dht;
bool valid = false;
float suhu = 0, kelembapan = 0;
unsigned long terakhir = 0;

void kirimSensor() {
  if (!valid) {
    server.send(503, "application/json", "{\"error\":\"sensor belum siap\"}");
    return;
  }
  String body = String("{\"suhu\":") + String(suhu, 1)
      + ",\"kelembapan\":" + String(kelembapan, 1) + "}";
  server.send(200, "application/json", body);
}

void setup() {
  Serial.begin(115200);
  dht.setup(15, DHTesp::DHT22);
  WiFi.mode(WIFI_STA);
  WiFi.begin("Wokwi-GUEST", "");
  unsigned long mulai = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - mulai < 15000) delay(250);
  server.on("/", HTTP_GET, []() { server.send(200, "text/plain", "Buka /sensor"); });
  server.on("/sensor", HTTP_GET, kirimSensor);
  server.begin();
}

void loop() {
  server.handleClient();
  if (millis() - terakhir >= 2000) {
    terakhir = millis();
    TempAndHumidity data = dht.getTempAndHumidity();
    valid = !isnan(data.temperature) && !isnan(data.humidity);
    if (valid) { suhu = data.temperature; kelembapan = data.humidity; }
  }
  delay(2);
}
