#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.I2CSwitch import I2CSwitch
from lib.POEController import POEController
from lib.POESwitch import POESwitch
from lib.SFP import SFP

I2C_BUS = 0

I2C_SW0_ADDR = 0x71
I2C_SW1_ADDR = 0x72

"""
I2C switch 0x72
   channel 0:     clock
   channel 1:     not used
   channel 2:     not used
   channel 3:     I2C switch 0x71

I2C switch 0x71
   channel 0:     poe
   channel 1:     sfp 1
   channel 2:     sfp 0
   channel 3:     not used
   
"""

I2C_POE0_ADDR = 0x20
I2C_POE1_ADDR = 0x22

I2C_SFP_ADDR = 0x50

###

isw1 = I2CSwitch(I2C_BUS, I2C_SW1_ADDR)
isw2 = I2CSwitch(I2C_BUS, I2C_SW0_ADDR)

pc1 = POEController(I2C_BUS, I2C_POE0_ADDR)
pc2 = POEController(I2C_BUS, I2C_POE1_ADDR)

### POE

isw1.select(3)
isw2.select(0)

sw = POESwitch()
sw.add_controller(pc1)
sw.add_controller(pc2)

print(sw.port_status(0))
print(sw.port_status(1))
try:
   print(sw.port_on(9))
except:
   print("index error")

print(sw.port_voltage(0))

print(sw.voltage_in(0))
print(sw.temperature(0))

sw.print()

### SFP 

sfp_id = 0
for mux_channel in [2, 1]:

   isw1.select(3)
   isw2.select(mux_channel)

   sfp = SFP(I2C_BUS, I2C_SFP_ADDR)

   print(f"SFP {sfp_id}")
   if sfp.is_available():
      print(f"\tvendor: {sfp.vendor()}")
      print(f"\tmodel: {sfp.model()}")
      print(f"\tserial: {sfp.serial()}")
      print(f"\tdatecode: {sfp.datecode()}")
      print(f"\tvoltage: {sfp.voltage()}V")
      print(f"\ttemperature: {sfp.temperature()}C")
      print(f"\ttx bias: {sfp.tx_bias()}mA")
      print(f"\ttx power: {sfp.tx_power()}uW")
      print(f"\trx power: {sfp.rx_power()}uW")
   else:
      print("\tnot available")

   sfp_id += 1
