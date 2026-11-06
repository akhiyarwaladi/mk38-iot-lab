#include <Arduino.h>
#include <DHTesp.h>
#include "aturan.h"
#include "uji_aturan.h"

const int LED_PIN = 23;
DHTesp dht;
bool nyala = false;

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  if (!ujiAturan(LED_PIN)) {
    while (true) delay(1000);
  }
  dht.setup(15, DHTesp::DHT22);
  delay(2000);
}

void loop() {
  TempAndHumidity data = dht.getTempAndHumidity();
  nyala = keadaanBerikut(data.temperature, nyala);
  digitalWrite(LED_PIN, nyala ? HIGH : LOW);
  Serial.printf("Suhu=%.1f C LED=%s GPIO=%d\r\n", data.temperature,
                nyala ? "nyala" : "mati", digitalRead(LED_PIN));
  delay(2000);
}
