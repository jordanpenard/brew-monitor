# brew-monitor Hardware

## Bill of materials
- Micro controller : WeMos D1 Mini
- Accelerometer : MPU-6050
- Batterie charger : TP4056
- Batterie : Panasonic 18650

## Wiring
- D0 and RST pins of D1 mini connect through 200 Ohms resistor
- SCL of the MPU connect to D3 pin of D1 mini
- SDA of the MPU connect to D4 pin of D1 mini
- VCC and GND pins of D1 mini and MPU connects to the batterie via a switch
- 2 100k reistors in series connected between VCC and GND, with the mid point connected to A0 pin of D1 mini
- TP4056 directly connects to the batterie

# brew-monitor Software

Software running on the micro controller.

## Dependencies
- Arduino IDE
- ESP8266 board package

## Arduino libraries
- Wire
