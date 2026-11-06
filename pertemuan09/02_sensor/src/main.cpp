#include <Arduino.h>
#include <DHTesp.h>

DHTesp dht;

void setup() {
  Serial.begin(115200);
  dht.setup(15, DHTesp::DHT22);
  delay(2000);
}

void loop() {
  TempAndHumidity data = dht.getTempAndHumidity();
  if (isnan(data.temperature) || isnan(data.humidity)) {
    Serial.println("Sensor gagal dibaca. Periksa GPIO 15.");
  } else {
    Serial.printf("Suhu: %.1f C | Kelembapan: %.1f %%\n",
                  data.temperature, data.humidity);
  }
  delay(2000);
}
