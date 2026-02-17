#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import time

from functools import partial
from lib.BMP585 import BMP585

from lib.I2CSwitch import I2CSwitch

#isw = I2CSwitch(0, 0x70, "a0080000.gpio", 0)
#isw.reset()

#bmp = BMP585(0, 0x47, False, (partial(isw.select, 5),))
bmp = BMP585(7, 0x47, True)

while True:
    temp, pressure = bmp.read()

    print(f"Temperature: {temp:.2f} °C")
    print(f"Pressure:   {pressure:.2f} Pa")
    print("--------------")

