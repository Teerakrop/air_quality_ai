/*
  Air Quality Sensor Interface for ESP32
  Supports: SDS011 (PM2.5, PM10), MQ135 (Gas), DHT22 (Temperature, Humidity)
  
  Connections:
  - SDS011: RX -> GPIO16, TX -> GPIO17
  - DHT22: Data -> GPIO4
  - MQ135: Analog -> GPIO36 (A0)
  
  Serial Communication Protocol:
  - Baud Rate: 115200
  - Commands: PING, READ
  - Response Format: JSON
*/

#include <WiFi.h>
#include <ArduinoJson.h>
#include <SoftwareSerial.h>
#include <DHT.h>

// Pin Definitions
#define SDS011_RX_PIN 16
#define SDS011_TX_PIN 17
#define DHT22_PIN 4
#define MQ135_PIN 36

// Sensor Initialization
SoftwareSerial sds011(SDS011_RX_PIN, SDS011_TX_PIN);
DHT dht(DHT22_PIN, DHT22);

// Global Variables
float pm25 = 0.0;
float pm10 = 0.0;
float temperature = 0.0;
float humidity = 0.0;
int gasLevel = 0;

// Timing
unsigned long lastSensorRead = 0;
const unsigned long SENSOR_READ_INTERVAL = 2000; // 2 seconds

// SDS011 Commands
byte sds011_sleep_cmd[] = {0xAA, 0xB4, 0x06, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x05, 0xAB};
byte sds011_wakeup_cmd[] = {0xAA, 0xB4, 0x06, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x06, 0xAB};

void setup() {
  // Initialize Serial Communication
  Serial.begin(115200);
  while (!Serial) {
    delay(10);
  }
  
  // Initialize Sensors
  sds011.begin(9600);
  dht.begin();
  
  // Initialize analog pin
  pinMode(MQ135_PIN, INPUT);
  
  // Wake up SDS011
  sds011.write(sds011_wakeup_cmd, sizeof(sds011_wakeup_cmd));
  
  Serial.println("ESP32 Air Quality Sensor Interface Ready");
  Serial.println("Commands: PING, READ");
  
  delay(2000); // Allow sensors to stabilize
}

void loop() {
  // Handle Serial Commands
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "PING") {
      Serial.println("PONG");
    }
    else if (command == "READ") {
      readAllSensors();
      sendSensorData();
    }
    else {
      Serial.println("{\"error\":\"Unknown command\"}");
    }
  }
  
  // Periodic sensor reading (for internal use)
  if (millis() - lastSensorRead > SENSOR_READ_INTERVAL) {
    readAllSensors();
    lastSensorRead = millis();
  }
  
  delay(100);
}

void readAllSensors() {
  // Read SDS011 (PM2.5 and PM10)
  readSDS011();
  
  // Read DHT22 (Temperature and Humidity)
  readDHT22();
  
  // Read MQ135 (Gas Level)
  readMQ135();
}

void readSDS011() {
  byte buffer[10];
  int index = 0;
  
  // Clear any existing data
  while (sds011.available()) {
    sds011.read();
  }
  
  // Wait for data
  unsigned long startTime = millis();
  while (sds011.available() < 10 && millis() - startTime < 1000) {
    delay(10);
  }
  
  if (sds011.available() >= 10) {
    // Read 10 bytes
    for (int i = 0; i < 10; i++) {
      buffer[i] = sds011.read();
    }
    
    // Validate header and tail
    if (buffer[0] == 0xAA && buffer[1] == 0xC0 && buffer[9] == 0xAB) {
      // Calculate PM values
      pm25 = ((buffer[3] << 8) | buffer[2]) / 10.0;
      pm10 = ((buffer[5] << 8) | buffer[4]) / 10.0;
      
      // Validate ranges
      if (pm25 < 0 || pm25 > 999.9) pm25 = 0.0;
      if (pm10 < 0 || pm10 > 999.9) pm10 = 0.0;
    }
  } else {
    // No data available, keep previous values or set to error values
    // pm25 and pm10 retain their previous values
  }
}

void readDHT22() {
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  
  // Check if readings are valid
  if (!isnan(temp) && !isnan(hum)) {
    temperature = temp;
    humidity = hum;
  }
  // If invalid, keep previous values
}

void readMQ135() {
  // Read analog value from MQ135
  int rawValue = analogRead(MQ135_PIN);
  
  // Convert to gas level (0-1000 scale)
  // This is a simplified conversion - in practice, you'd calibrate this
  gasLevel = map(rawValue, 0, 4095, 0, 1000);
  
  // Ensure reasonable range
  if (gasLevel < 0) gasLevel = 0;
  if (gasLevel > 1000) gasLevel = 1000;
}

void sendSensorData() {
  // Create JSON document
  StaticJsonDocument<200> doc;
  
  doc["pm25"] = round(pm25 * 10) / 10.0;  // Round to 1 decimal place
  doc["pm10"] = round(pm10 * 10) / 10.0;
  doc["temperature"] = round(temperature * 10) / 10.0;
  doc["humidity"] = round(humidity * 10) / 10.0;
  doc["gas_level"] = gasLevel;
  
  // Serialize and send
  String jsonString;
  serializeJson(doc, jsonString);
  Serial.println(jsonString);
}

// Utility function for debugging
void printSensorValues() {
  Serial.print("PM2.5: "); Serial.print(pm25); Serial.print(" μg/m³, ");
  Serial.print("PM10: "); Serial.print(pm10); Serial.print(" μg/m³, ");
  Serial.print("Temp: "); Serial.print(temperature); Serial.print(" °C, ");
  Serial.print("Humidity: "); Serial.print(humidity); Serial.print(" %, ");
  Serial.print("Gas: "); Serial.println(gasLevel);
}

// Function to put SDS011 to sleep (for power saving)
void sleepSDS011() {
  sds011.write(sds011_sleep_cmd, sizeof(sds011_sleep_cmd));
  delay(100);
}

// Function to wake up SDS011
void wakeupSDS011() {
  sds011.write(sds011_wakeup_cmd, sizeof(sds011_wakeup_cmd));
  delay(2000); // Wait for sensor to stabilize
}
