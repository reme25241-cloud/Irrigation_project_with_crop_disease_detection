#include <WiFi.h>
#include <HTTPClient.h>
#include <DHT.h>

/* ===================== WIFI ===================== */
const char* ssid = "qwerty";
const char* password = ".12345678.";

/* ===================== DJANGO API ===================== */
const char* SERVER_URL =
"https://irrigation-project-with-crop-disease.onrender.com/alerts/api/iot-alert/";

/* ===================== DHT22 ===================== */
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

/* ===================== SOIL SENSORS ===================== */
#define SOIL1_PIN 34
#define SOIL2_PIN 35
#define SOIL3_PIN 32
#define SOIL_THRESHOLD 2000   // Adjust after calibration

/* ===================== RELAYS (ACTIVE LOW) ===================== */
#define RELAY1 23
#define RELAY2 22
#define RELAY3 21

/* ===================== RELAY TIMINGS ===================== */
#define RELAY1_TIME 3000   // 3 sec
#define RELAY2_TIME 5000   // 5 sec
#define RELAY3_TIME 7000   // 7 sec

/* ===================== ALERT CONTROL ===================== */
unsigned long lastAlertTime = 0;
const unsigned long ALERT_INTERVAL = 5 * 60 * 1000; // 5 minutes

/* ====================================================== */

void connectWiFi() {
  Serial.print("🔌 Connecting to WiFi");
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("\n✅ WiFi Connected");
  Serial.print("📡 IP Address: ");
  Serial.println(WiFi.localIP());
}

/* ====================================================== */

void sendAlert(int soil, float temp, float hum, int relayNo) {
  if (WiFi.status() != WL_CONNECTED) return;

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");

  String payload = "{";
  payload += "\"soil\":" + String(soil) + ",";
  payload += "\"temperature\":" + String(temp) + ",";
  payload += "\"humidity\":" + String(hum) + ",";
  payload += "\"relay\":\"Relay " + String(relayNo) + "\"";
  payload += "}";

  int httpCode = http.POST(payload);

  Serial.print("📤 Alert sent | HTTP Code: ");
  Serial.println(httpCode);

  http.end();
}

/* ====================================================== */

void runRelayTimed(int relayPin, unsigned long durationMs) {
  digitalWrite(relayPin, LOW);   // Relay ON (ACTIVE LOW)
  delay(durationMs);
  digitalWrite(relayPin, HIGH);  // Relay OFF
}

/* ====================================================== */

void setup() {
  Serial.begin(115200);
  delay(1000);

  dht.begin();

  pinMode(RELAY1, OUTPUT);
  pinMode(RELAY2, OUTPUT);
  pinMode(RELAY3, OUTPUT);

  // Relays OFF at startup
  digitalWrite(RELAY1, HIGH);
  digitalWrite(RELAY2, HIGH);
  digitalWrite(RELAY3, HIGH);

  connectWiFi();

  Serial.println("🚀 ESP32 Smart Irrigation System Started");
}

/* ====================================================== */

void loop() {
  // ---- Read soil sensors ----
  int soil1 = analogRead(SOIL1_PIN);
  int soil2 = analogRead(SOIL2_PIN);
  int soil3 = analogRead(SOIL3_PIN);

  // ---- Read DHT22 ----
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("❌ Failed to read from DHT22!");
    delay(2000);
    return;
  }

  // ---- Serial Monitoring ----
  Serial.println("=================================");
  Serial.print("🌡 Temp: "); Serial.print(temperature);
  Serial.print(" °C | 💧 Humidity: "); Serial.print(humidity);
  Serial.println(" %");

  Serial.print("🌱 Soil 1: "); Serial.println(soil1);
  Serial.print("🌱 Soil 2: "); Serial.println(soil2);
  Serial.print("🌱 Soil 3: "); Serial.println(soil3);

  // ---- Irrigation Logic ----
  if (soil1 > SOIL_THRESHOLD) {
    Serial.println("🚰 Soil 1 Dry → Relay 1 ON for 3 sec");
    runRelayTimed(RELAY1, RELAY1_TIME);
    sendAlert(soil1, temperature, humidity, 1);
  }

  if (soil2 > SOIL_THRESHOLD) {
    Serial.println("🚰 Soil 2 Dry → Relay 2 ON for 5 sec");
    runRelayTimed(RELAY2, RELAY2_TIME);
    sendAlert(soil2, temperature, humidity, 2);
  }

  if (soil3 > SOIL_THRESHOLD) {
    Serial.println("🚰 Soil 3 Dry → Relay 3 ON for 7 sec");
    runRelayTimed(RELAY3, RELAY3_TIME);
    sendAlert(soil3, temperature, humidity, 3);
  }

  // ---- High Temperature Alert ----
  unsigned long now = millis();
  if (temperature > 40 && now - lastAlertTime > ALERT_INTERVAL) {
    Serial.println("🔥 High Temperature Alert!");
    sendAlert(0, temperature, humidity, 0);
    lastAlertTime = now;
  }

  delay(5000); // Main loop delay
}
