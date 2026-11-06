#pragma once
#include <math.h>

inline bool keadaanBerikut(float suhu, bool sebelumnya) {
  if (!isfinite(suhu) || suhu < -40.0f || suhu > 80.0f) return false;
  if (suhu >= 30.0f) return true;
  if (suhu <= 28.0f) return false;
  return sebelumnya;
}
