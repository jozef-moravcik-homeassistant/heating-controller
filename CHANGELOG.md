# Heating Controller

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/jozef-moravcik-homeassistant/heating-controller)](https://github.com/jozef-moravcik-homeassistant/heating-controller/releases)

Home Assistant integration for controlling heating systems with heat pump, accumulation tanks (ACC) and domestic hot water (DHW).

## v1.02.06
### Fixes:
- The display of two integer number entities number.heating_controller_dhw_target_temperature and number.heating_controller_acc_target_temperature has changed, the decimal number is no longer displayed.

## v1.02.05
### Five new sensors have been added to measure stored energy in water tanks:
- sensor.heating_controller_dhw_stored_energy
- sensor.heating_controller_acc_stored_energy
- sensor.heating_controller_acc1_stored_energy
- sensor.heating_controller_acc2_stored_energy
- sensor.heating_controller_total_stored_energy

### Changes:
- number.heating_controller_dhw_target_temperature was changed from SLIDER to BOX
- number.heating_controller_acc_target_temperature was changed from SLIDER to BOX


## v1.02.04

### Fixes:
- Checking sensor availability after HA start/restart


## v1.02.03
In real-operation use, it was found that some boiler designs do not use check valves at the ACC outlets, which causes water circulation that also passes through the ACC outlets when the DHW tank is heated by the heat pump. This results in the water in the ACC also heating up during DHW heating, which significantly slows down DHW heating. 
This version solves this situation by closing the ACC outlet valves in strict mode during DHW heating by the heat pump, thus blocking unwanted circulation of water from DHW. 
However, if the heating (thermostat) is "ON" during DHW heating, the Heating Controller interrupts the heating by closing the ACC outlet valves, the circulation and auxiliary pumps are also turned off, and the heating is turned on only after DHW heating is complete. 
Since the DHW tank is usually many times smaller than the ACC tank and its heating does not take long (30 - 60 minutes), I accepted a temporary interruption of heating, which the user will not even notice, especially with underfloor heating.
If check valves are installed in the system, the valve control mode can be switched to Moderate or Generic, in these modes the outlet valves will not close during DHW heating.

## v1.02.02

### Fixes:
- 1. Improved method for updating sensor status
- 2. Integration settings have been improved
 
### New Features:
- 1. Sensors ACC 1 - ON/OFF ,  ACC 2 - ON/OFF ,  Automatic Mode ,  HP to DHW  and  Heating Source ON/OFF got off-status icons


## v1.02.01

### Hysteresis has been implemented for the minimum temperature in ACC usable for heating.
The hysteresis has a fixed value of 2 degrees. 
So if you set the minimum temperature in ACC usable for heating to 35 degrees Celsius in the configuration and when the temperature rises and reaches in ACC = 35 degrees, 
the system enables heating. If the temperature in ACC drops below 33 degrees Celsius, the system disables heating (the ACC outlet valves close).

### Two new sensors have been added:
####  1.  sensor.heating_controller_current_operating_mode indicates ID of a current operating mode of the heating controller logic. All IDs are listed in this table:

-  -1 = "Error"
-   0 = "Undefined"
-   1 = "Idle"
-   2 = "Heating ACC"
-   3 = "Heating DHW"
-   4 = "Heating DHW from ACC (pumping water only)"
-   5 = "Heating ACC + DHW from ACC (water pumping)"
-   6 = "Heating DHW + DHW from ACC (water pumping)"

####  2.  sensor.heating_controller_current_operating_mode_text indicates TEXT value of a current operating mode

### In the operating modes "Cycle: 1.PDHW > 2.DHW" and "Cycle: 1.P-DHW > 2.DHW > 3.ACC" protection against cycling of the heating source on and off was created,
 which happened when DHW heating from ACC was started, the temperatures equalized and the system switched to DHW heating from the heating source. 
 When the heating source (for example, a heat pump) mixed a water in the DHW tank in which there was cold water in the lower part and hot water in the upper part, 
 the temperature sensor registered a decrease in the averrage temperature in the upper part and then the system switched back to the mode of pumping water from ACC to DHW,
 which turned off the heating source, when the temperatures equalized, the heating source was turned on again and the cycle was repeated several times until
 a uniform temperature was reached throughout the tank, then DHW heating continued. 
 To prevent repeated switching of the heating source on and off, now, when the DHW is heated from the ACC and switched to heating the DHW from the heating source, 
 the transfer from the ACC to the DHW is be blocked until the target temperature is reached in the DHW.
 

 






