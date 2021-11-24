# brew-monitor

Monitoring system for beer fermentation. It tracks gravity and temperature of the beer while it is fermenting.
The idea came from the iSpindel project : https://github.com/universam1/iSpindel

## Hardware

The [hardware](hardware/README.md) folder has all the information about how to build the sensor and the arduino code to use.

The sensor regularly reads the temperature and angle and sends it to the website to store.

## Website

The [website](website/README.md) is providing an API that the sensor can contact to store and and a UI for the users to see the information. 

