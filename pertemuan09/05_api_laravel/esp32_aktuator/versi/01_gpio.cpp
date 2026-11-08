#include <Arduino.h>

void sudutServo(int sudut) {
  uint32_t pulsaUs = map(sudut, 0, 180, 500, 2500);
  ledcWrite(0, (pulsaUs * 65535UL + 10000UL) / 20000UL);
}

void setup() {
  Serial.begin(115200);
  pinMode(23, OUTPUT);
  digitalWrite(23, LOW);
  ledcSetup(0, 50, 16);
  ledcAttachPin(18, 0);
  sudutServo(0);
}

void loop() {
  for (int sudut : {0, 90, 180}) {
    digitalWrite(23, sudut == 0 ? LOW : HIGH);
    sudutServo(sudut);
    Serial.printf("Uji lokal: servo=%d LED=%d\n", sudut, digitalRead(23));
    delay(2000);
  }
}
