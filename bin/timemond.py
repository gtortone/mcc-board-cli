#!/usr/bin/env python3

import gpiod
import select
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.I2CSwitch import I2CSwitch
from lib.Si5345 import Si5345
from functools import partial

I2C_SI5342_BUS = 6
SI5342_I2C_ADDR = 0x68

# input pin
IN_GPIO_BANK = "a0130000.gpio" 
IN_GPIO_LINE = 0     # Timing link lock

chip_in = gpiod.Chip(f"{IN_GPIO_BANK}")
line_in = chip_in.get_line(IN_GPIO_LINE)

line_in.request(consumer="pl_timing_lock", type=gpiod.LINE_REQ_EV_FALLING_EDGE) 

pll = Si5345(I2C_SI5342_BUS, SI5342_I2C_ADDR)

poller = select.poll()
poller.register(line_in.event_get_fd(), select.POLLIN)

while True:

   poller.poll()

   ev = line_in.event_read()
   print(f"ts:{ev.sec}.{ev.nsec} falling edge - reset PLL chip")
   pll.reset()
