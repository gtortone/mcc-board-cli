#!/usr/bin/env python3

import gpiod
import select
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.I2CSwitch import I2CSwitch
from lib.Si5345 import Si5345
from functools import partial

I2C_BUS = 0
I2C_SW_ADDR = 0x70

SI5342_MUX_CHANNEL = 4
SI5342_I2C_ADDR = 0x68

# input pin
IN_GPIO_BANK = "a0130000.gpio" 
IN_GPIO_LINE = 0     # Timing link lock

chip_in = gpiod.Chip(f"{IN_GPIO_BANK}")
line_in = chip_in.get_line(IN_GPIO_LINE)

line_in.request(consumer="pl_timing_lock", type=gpiod.LINE_REQ_EV_FALLING_EDGE) 

isw = I2CSwitch(I2C_BUS, I2C_SW_ADDR, "a0080000.gpio", 0)
isw.reset()

pll = Si5345(I2C_BUS , SI5342_I2C_ADDR, (partial(isw.select, SI5342_MUX_CHANNEL),))

poller = select.poll()
poller.register(line_in.event_get_fd(), select.POLLIN)

while True:

   poller.poll()

   print(f"ts:{ev.sec}.{ev.nsec} falling edge - reset PLL chip")
   pll.reset()
