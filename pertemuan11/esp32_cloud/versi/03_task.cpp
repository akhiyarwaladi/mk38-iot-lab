#include <Arduino.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

unsigned long terakhir = 0;

void pengingat(void*) {
  for (;;) {
    Serial.println("TASK pengingat");
    vTaskDelay(pdMS_TO_TICKS(1000));
  }
}

void setup() {
  Serial.begin(115200);
  if (xTaskCreatePinnedToCore(pengingat, "pengingat", 4096, nullptr, 1, nullptr, 1) != pdPASS)
    Serial.println("Task gagal dibuat");
}

void loop() {
  if (millis() - terakhir >= 2000) {
    terakhir = millis();
    Serial.println("MAIN loop");
  }
  delay(2);
}
