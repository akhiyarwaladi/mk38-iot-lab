#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include <DHTesp.h>

WebServer server(80);
DHTesp dht;
const int LED_PIN = 23;
bool ledMenyala = false;
bool sensorValid = false;
float suhu = 0;
float kelembapan = 0;
unsigned long terakhirBaca = 0;

const char PAGE[] PROGMEM = R"HTML(
<!doctype html><html lang="id"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kendali LED ESP32</title>
<h1>Kendali LED ESP32</h1>
<p>LED terhubung ke GPIO 23.</p>
<form action="/led" method="post">
  <button name="state" value="on">Nyalakan LED</button>
  <button name="state" value="off">Matikan LED</button>
</form>
<p><a href="/sensor">Baca JSON sensor</a></p>
</html>)HTML";

void kirimSensor() {
  if (!sensorValid) {
    server.send(503, "application/json", "{\"error\":\"sensor belum siap\"}");
    return;
  }
  String body = String("{\"suhu\":") + String(suhu, 1) +
      ",\"kelembapan\":" + String(kelembapan, 1) +
      ",\"led\":" + (ledMenyala ? "true" : "false") + "}";
  server.send(200, "application/json", body);
}

void ubahLed() {
  String state = server.arg("state");
  if (state != "on" && state != "off") {
    server.send(400, "application/json", "{\"error\":\"state harus on/off\"}");
    return;
  }
  ledMenyala = state == "on";
  digitalWrite(LED_PIN, ledMenyala ? HIGH : LOW);
  Serial.println(ledMenyala ? "LED ON" : "LED OFF");
  server.sendHeader("Location", "/");
  server.send(303, "text/plain", "Kembali ke halaman kendali");
}

void setup() {
  Serial.begin(115200);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  dht.setup(15, DHTesp::DHT22);
  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  WiFi.begin("Wokwi-GUEST", "");
  unsigned long mulai = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - mulai < 15000) {
    delay(250);
  }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Wi-Fi belum tersambung. Periksa koneksi simulator.");
  }
  server.on("/", HTTP_GET, []() { server.send(200, "text/html", PAGE); });
  server.on("/sensor", HTTP_GET, kirimSensor);
  server.on("/led", HTTP_POST, ubahLed);
  server.onNotFound([]() { server.send(404, "text/plain", "Rute tidak ditemukan"); });
  server.begin();
  Serial.print("IP ESP32: ");
  Serial.println(WiFi.localIP());
  Serial.println("Wokwi VS Code: buka http://localhost:8180");
}

void loop() {
  server.handleClient();
  if (millis() - terakhirBaca >= 2000) {
    terakhirBaca = millis();
    TempAndHumidity data = dht.getTempAndHumidity();
    sensorValid = !isnan(data.temperature) && !isnan(data.humidity);
    if (sensorValid) {
      suhu = data.temperature;
      kelembapan = data.humidity;
    }
  }
  delay(2);
}
