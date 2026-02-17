#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from functools import partial
from time import sleep

from lib.I2CSwitch import I2CSwitch

from lib.INA238 import INA238

def read():
    print("Bus Voltage    : %.3f V" % ina.voltage())
    print("Bus Current    : %.3f A" % ina.current())
    print("Supply Voltage : %.3f V" % ina.supply_voltage())
    print("Shunt voltage  : %.3f mV" % ina.shunt_voltage())
    print("Power          : %.3f W" % ina.power())

if __name__ == "__main__":

   #isw = I2CSwitch(0, 0x70, "a0080000.gpio", 0)
   #isw.reset()

   #ina = INA238(0, 0x40, 0.02, 10, (partial(isw.select, 3),))
   ina = INA238(5, 0x40, 0.02, 10)

   while True:
      read()
      print("===================================================")
      sleep(0.2)
