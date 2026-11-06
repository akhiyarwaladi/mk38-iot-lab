#include <Arduino.h>
#include <WiFi.h>

const char* SSID = "Wokwi-GUEST";
const char* PASSWORD = "";

void setup() {
  Serial.begin(115200);
  WiFi.mode(WIFI_STA);
  WiFi.begin(SSID, PASSWORD);
  Serial.println("Menghubungkan Wi-Fi...");

  unsigned long mulai = millis();
  while (WiFi.status() != WL_CONNECTED &&
         millis() - mulai < 15000) {
    delay(250);
    Serial.print(".");
  }
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("\nIP ESP32: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\nGagal. Periksa SSID dan jalankan ulang.");
  }
}

void loop() {
  delay(100);
}
