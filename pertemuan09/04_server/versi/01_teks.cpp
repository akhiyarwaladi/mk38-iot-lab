#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>

WebServer server(80);

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin("Wokwi-GUEST", "");
  unsigned long mulai = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - mulai < 15000) delay(250);
  server.on("/", HTTP_GET, []() {
    server.send(200, "text/plain", "ESP32 siap");
  });
  server.begin();
  Serial.println("Buka http://localhost:8180 melalui gateway VS Code.");
}

void loop() {
  server.handleClient();
  delay(2);
}
