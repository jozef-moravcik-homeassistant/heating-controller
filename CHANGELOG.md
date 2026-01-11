# Heating Controller

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/v/release/jozef-moravcik-homeassistant/heating-controller)](https://github.com/jozef-moravcik-homeassistant/heating-controller/releases)

Home Assistant integration for controlling heating systems with heat pump, accumulation tanks (ACC) and domestic hot water (DHW).

## v1.02.01

# Hysteresis has been implemented for the minimum temperature in ACC usable for heating.
The hysteresis has a fixed value of 2 degrees. 
So if you set the minimum temperature in ACC usable for heating to 35 degrees Celsius in the configuration and when the temperature rises and reaches in ACC = 35 degrees, 
the system enables heating. If the temperature in ACC drops below 33 degrees Celsius, the system disables heating (the ACC outlet valves close).

# Two new sensors have been added:
1. sensor.heating_controller_current_operating_mode indicates ID of a current operating mode of the heating controller logic. All IDs are listed in this table:

  # -1 = "Error"
  # 0 = "Undefined"
  # 1 = "Idle"
  # 2 = "Heating ACC"
  # 3 = "Heating DHW"
  # 4 = "Heating DHW from ACC (pumping water only)"
  # 5 = "Heating ACC + DHW from ACC (water pumping)"
  # 6 = "Heating DHW + DHW from ACC (water pumping)"

2. sensor.heating_controller_current_operating_mode_text indicates TEXT value of a current operating mode

# In the operating modes "Cycle: 1.PDHW > 2.DHW" and "Cycle: 1.P-DHW > 2.DHW > 3.ACC" protection against cycling of the heating source on and off was created,
 which happened when DHW heating from ACC was started, the temperatures equalized and the system switched to DHW heating from the heating source. 
 When the heating source (for example, a heat pump) mixed a water in the DHW tank in which there was cold water in the lower part and hot water in the upper part, 
 the temperature sensor registered a decrease in the averrage temperature in the upper part and then the system switched back to the mode of pumping water from ACC to DHW,
 which turned off the heating source, when the temperatures equalized, the heating source was turned on again and the cycle was repeated several times until
 a uniform temperature was reached throughout the tank, then DHW heating continued. 
 To prevent repeated switching of the heating source on and off, now, when the DHW is heated from the ACC and switched to heating the DHW from the heating source, 
 the transfer from the ACC to the DHW is be blocked until the target temperature is reached in the DHW.
 

 
