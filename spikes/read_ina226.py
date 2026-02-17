#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from functools import partial
from time import sleep

from lib.I2CSwitch import I2CSwitch

from lib.INA226 import INA226

def read():
    print("Bus Voltage    : %.3f V" % ina.voltage())
    print("Bus Current    : %.3f A" % ina.current())
    print("Supply Voltage : %.3f V" % ina.supply_voltage())
    print("Shunt voltage  : %.3f mV" % ina.shunt_voltage())
    print("Power          : %.3f W" % ina.power())

if __name__ == "__main__":

   #isw = I2CSwitch(0, 0x70, "a0080000.gpio", 0)
   #isw.reset()

   #ina = INA226(0, 0x41, 0.02, (partial(isw.select, 3),))
   ina = INA226(4, 0x41, 0.02)
   ina.configure(avg_mode=INA226.AVG_16BIT)

   while True:
      if ina.is_conversion_ready():
         read()
         print("===================================================")
      sleep(0.2)
