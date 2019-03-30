# brew-monitor

Monitoring system for beer fermentation. It tracks gravity and temperature of the beer while it is fermenting.
The idea came from the iSpindel project : https://github.com/universam1/iSpindel

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
- TP4056 directly connects to the batterie
