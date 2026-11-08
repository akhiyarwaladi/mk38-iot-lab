#include "actuator_client.h"

Aktuator lampu{"lampu", "led"};
Aktuator pintu{"pintu", "servo"};
unsigned long cek = 0, lapor = 0;

void terapkanLed(int nilai) { digitalWrite(23, nilai ? HIGH : LOW); }

void terapkanServo(int sudut) {
  uint32_t pulsaUs = map(sudut, 0, 180, 500, 2500);
  uint32_t duty = (pulsaUs * 65535UL + 10000UL) / 20000UL;
  ledcWrite(0, duty);
  Serial.printf("PWM servo=%d pulsa_us=%lu duty=%lu\n", sudut, (unsigned long)pulsaUs, (unsigned long)ledcRead(0));
}

void setup() {
  Serial.begin(115200);
  pinMode(23, OUTPUT);
  terapkanLed(0);
  ledcSetup(0, 50, 16);
  ledcAttachPin(18, 0);
  terapkanServo(0);
  mulaiWifi();
}

void loop() {
  if (!wifiSiap()) { delay(10); return; }
  if (millis() - cek >= 1000) {
    cek = millis();
    periksa(lampu, terapkanLed);
    periksa(pintu, terapkanServo);
  }
  if (millis() - lapor >= 10000) {
    lapor = millis();
    heartbeat(lampu);
    heartbeat(pintu);
  }
  delay(10);
}
