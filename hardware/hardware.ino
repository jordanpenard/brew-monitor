/*
 *  brew-monitor Hardware
 *
 *
 */

#include <ESP8266WiFi.h>
#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#include "hardware.h"

// Data wire is plugged into port 2 on the Arduino
#define ONE_WIRE_BUS 2

// Server to send an Hello word to
#define SERVER 192,168,0,10
#define PORT 8080

// Address of the accelerometer
#define MPU 0x68

// Setup the bus for the temp sensor
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

IPAddress server(SERVER);
WiFiClient client;
  

void setup() {
  Serial.begin(115200);
  Wire.begin();
}

void loop() {
  long AcX,AcY,AcZ,Tmp;
  float X, Y, Z, Xangle;

  Serial.println();
  Serial.print("Connecting to WIFI");
  
  // Connecting to a WiFi network
  WiFi.begin(SSID, PASSWORD);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");  
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
  
  // Create TCP connections
  if (!client.connect(server, PORT)) {
    Serial.println("connection failed");
    return;
  }
  
  client.println("Hello world");
  
  // Start-up the accelerometer
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0);    // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);

  // Get accelerometer data
  Wire.beginTransmission(MPU);
  Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
  Wire.endTransmission(false);
  Wire.requestFrom((uint8_t)MPU, (size_t)8, true);  // request a total of 8 registers
  AcX = Wire.read()<<8|Wire.read();  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)    
  AcY = Wire.read()<<8|Wire.read();  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
  AcZ = Wire.read()<<8|Wire.read();  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
  Tmp = Wire.read()<<8|Wire.read();  // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)

  // Put the accelerometer in sleep mode
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0x40);    // set bit 6 to 1 (sleep mode)
  Wire.endTransmission(true);

  // Compute G forces on each axis
  X = AcX/16384.0;
  Y = AcY/16384.0;
  Z = AcZ/16384.0;

  // Computing the X angle : arctan(X/sqrt(Y^2+Z^2))  
  Xangle = atan(X/sqrt(pow(Y,2)+pow(Z,2)));

  // Read temp sensor
  sensors.begin();
  sensors.requestTemperatures(); // Send the command to get temperatures
  float tempC = sensors.getTempCByIndex(0);

  Serial.println();
  Serial.println("MPU-6050 :");
  Serial.print(" X = "); Serial.println(X);
  Serial.print(" Y = "); Serial.println(Y);
  Serial.print(" Z = "); Serial.println(Z);
  Serial.print(" Tmp = "); Serial.println(Tmp/340.00+36.53);  //equation for temperature in degrees C from datasheet
  Serial.print(" Xangle = "); Serial.println(Xangle);
  Serial.println("DS18B20");
  Serial.print(" Temperature : "); Serial.println(tempC);

  ESP.deepSleep(30e6); 
}
