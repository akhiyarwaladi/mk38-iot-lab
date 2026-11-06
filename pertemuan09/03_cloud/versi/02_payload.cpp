#include <Arduino.h>
#include <DHTesp.h>

DHTesp dht;

void setup() {
  Serial.begin(115200);
  dht.setup(15, DHTesp::DHT22);
}

void loop() {
  TempAndHumidity data = dht.getTempAndHumidity();
  if (!isnan(data.temperature) && !isnan(data.humidity)) {
    String payload = String("{\"field1\":") + String(data.temperature, 1)
        + ",\"field2\":" + String(data.humidity, 1) + "}";
    Serial.println(payload);
  }
  delay(2000);
}
