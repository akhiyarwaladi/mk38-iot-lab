#pragma once
#include <Arduino.h>
#include "aturan.h"

inline bool ujiAturan(int pin) {
  struct Kasus { float suhu; bool sebelum; bool harapan; };
  const Kasus kasus[] = {
    {27, false, false}, {30, false, true}, {29, true, true},
    {28, true, false}, {29, false, false}, {NAN, true, false},
    {90, true, false}, {-41, true, false}, {80, false, true},
    {-40, true, false}
  };
  for (const Kasus& uji : kasus) {
    bool hasil = keadaanBerikut(uji.suhu, uji.sebelum);
    digitalWrite(pin, hasil ? HIGH : LOW);
    if (hasil != uji.harapan || (digitalRead(pin) == HIGH) != hasil) {
      Serial.println("UJI ATURAN GAGAL; periksa logika dan GPIO.");
      digitalWrite(pin, LOW);
      return false;
    }
  }
  digitalWrite(pin, LOW);
  Serial.println("UJI ATURAN 10/10 LULUS; GPIO=LOW");
  return true;
}
