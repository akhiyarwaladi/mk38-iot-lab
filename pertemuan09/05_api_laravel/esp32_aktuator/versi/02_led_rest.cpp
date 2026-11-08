#include "actuator_client.h"

Aktuator lampu{"lampu", "led"};
unsigned long cek = 0, lapor = 0;

void terapkanLed(int nilai) { digitalWrite(23, nilai ? HIGH : LOW); }

void setup() {
  Serial.begin(115200);
  pinMode(23, OUTPUT);
  terapkanLed(0);
  mulaiWifi();
}

void loop() {
  if (!wifiSiap()) { delay(10); return; }
  if (millis() - cek >= 1000) { cek = millis(); periksa(lampu, terapkanLed); }
  if (millis() - lapor >= 10000) { lapor = millis(); heartbeat(lampu); }
  delay(10);
}
