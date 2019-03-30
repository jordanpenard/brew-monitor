/*
 *  brew-monitor Hardware
 *
 *
 */

#include <ESP8266WiFi.h>
#include <Wire.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#include "config.h"
  

void setup() {
  Serial.begin(115200);
  Serial.println();

  Wire.begin(MPU_SCL, MPU_SDA);
}

void connect_to_wifi() {
  
  Serial.println();
  Serial.print("Connecting to WIFI");
  
  // Connecting to a WiFi network
  WiFi.begin(SSID, PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    static int i = 0;

    delay(500);
    Serial.print(".");

    // If the connection takes too long, reset the board
    if (i > 20)
      ESP.restart();
    else
      i++;
  }

  Serial.println(" connected");  
  //Serial.print("IP address: ");
  //Serial.println(WiFi.localIP());
}

void http_get_request(const char* hostname, uint16_t port, String request) {
  WiFiClient client;

  Serial.print(String("[Connecting to ") + hostname + String(" ... "));
  while (!client.connect(hostname, port)) {
    static int i = 0;
    
    Serial.println(String("connection failed, try ") + i + String("]"));
    delay(500);

    // If the connection takes too long, reset the board
    if (i > 20)
      ESP.restart();
    else
      i++;
  }
  
  Serial.println("connected]");
  Serial.println("[Sending a request]");
  client.print("GET /" + request + " HTTP/1.1\r\n" +
               "Host: " + hostname + "\r\n" +
               "Connection: close\r\n" +
               "\r\n");
  /*    
  Serial.println("[Response:]");
  while (client.connected() || client.available())
  {
    if (client.available())
    {
      String line = client.readStringUntil('\n');
      Serial.println(line);
    }
  }*/
  client.stop();
  Serial.println("[Disconnected]");
}

float filter(float data[NB_MEASURE]) {
  float out = 0;
  int count = 0;
  
  // Sort the array
  float tmp;
  for(int i = 0; i < NB_MEASURE; i++) {
    for(int j = i+1; j < NB_MEASURE; j++) {
      if (data[j] < data[i]) {
        tmp = data[j];
        data[j] = data[i];
        data[i] = tmp;
      }
    }
  }
  
  for(int i = 0; i < NB_MEASURE; i++) {
    if ((data[i] <= (data[NB_MEASURE/2]+G_FILTER)) && (data[i] >= (data[NB_MEASURE/2]-G_FILTER))) {
      out += data[i];
      count++;
    }    
  }

  float ret = out/count;

  if (ret > 1.0 || ret < -1.0) {
    Serial.println("---");
    Serial.println(String("High measurment : ") + ret);
    for(int i = 0; i < NB_MEASURE; i++) {
      Serial.println(data[i]);
    }
    Serial.println("---");
  }
  
  return ret;
}

void loop() {
  float AcX[NB_MEASURE];
  float AcY[NB_MEASURE];
  float AcZ[NB_MEASURE];
  float X, Y, Z, Tilt, Temp;
  
  // Start-up the accelerometer
  delay(100);
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0);    // set to zero (wakes up the MPU-6050)
  Wire.endTransmission(true);
  
  for(int i = 0; i < NB_MEASURE; i++) {
    // Get accelerometer data
    delay(100);
    Wire.beginTransmission(MPU);
    Wire.write(0x3B);  // starting with register 0x3B (ACCEL_XOUT_H)
    Wire.endTransmission(false);
    Wire.requestFrom((uint8_t)MPU, (size_t)8, true);  // request a total of 8 registers

    // Translate into G
    AcX[i] = (int16_t)(Wire.read()<<8|Wire.read())/MPU_1G;  // 0x3B (ACCEL_XOUT_H) & 0x3C (ACCEL_XOUT_L)    
    AcY[i] = (int16_t)(Wire.read()<<8|Wire.read())/MPU_1G;  // 0x3D (ACCEL_YOUT_H) & 0x3E (ACCEL_YOUT_L)
    AcZ[i] = (int16_t)(Wire.read()<<8|Wire.read())/MPU_1G;  // 0x3F (ACCEL_ZOUT_H) & 0x40 (ACCEL_ZOUT_L)
    
    // Translate into degree C and accumulate (for averaging)
    Temp += ((int16_t)(Wire.read()<<8|Wire.read())/340.00)+36.53; // 0x41 (TEMP_OUT_H) & 0x42 (TEMP_OUT_L)
  }

  // Put the accelerometer in sleep mode
  Wire.beginTransmission(MPU);
  Wire.write(0x6B); // PWR_MGMT_1 register
  Wire.write(0x40);    // set bit 6 to 1 (sleep mode)
  Wire.endTransmission(true);
  
  // Filter the readings
  X = filter(AcX);
  Y = filter(AcY);
  Z = filter(AcZ);

  // Compute the tilt  
  Tilt = (atan2(Y, sqrt(X * X + Z * Z))) * RAD_TO_DEG;

  // Average the temp values
  Temp = Temp/NB_MEASURE;
  
  //Serial.println("MPU-6050 :");
  //Serial.print(" X = "); Serial.println(X);
  //Serial.print(" Y = "); Serial.println(Y);
  //Serial.print(" Z = "); Serial.println(Z);
  Serial.print(" Tilt = "); Serial.println(Tilt);
  Serial.print(" Temp = "); Serial.println(Temp);

  connect_to_wifi();

  http_get_request(SERVER, PORT, String("submitTemperature?value=") + Tilt + String("&sensorID=10"));
  http_get_request(SERVER, PORT, String("submitTemperature?value=") + Temp + String("&sensorID=11"));

  // Sleep for 10 min
  ESP.deepSleep(60000000*10); 
}
