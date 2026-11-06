#!/usr/bin/env python3

import gpiod
from gpiod.line import Direction, Edge
import select
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.I2CSwitch import I2CSwitch
from lib.Si5345 import Si5345
from lib.gpiochip import open_chip
from functools import partial

I2C_SI5342_BUS = 6
SI5342_I2C_ADDR = 0x68

# input pin
IN_GPIO_BANK = "a0130000.gpio"
IN_GPIO_LINE = 0     # Timing link lock

chip_in = open_chip(f"{IN_GPIO_BANK}")

line_in = chip_in.request_lines(
   consumer="pl_timing_lock",
   config={IN_GPIO_LINE: gpiod.LineSettings(direction=Direction.INPUT,
                                            edge_detection=Edge.FALLING)})

pll = Si5345(I2C_SI5342_BUS, SI5342_I2C_ADDR)

poller = select.poll()
poller.register(line_in.fd, select.POLLIN)

while True:

   poller.poll()

   for ev in line_in.read_edge_events():
      sec, nsec = divmod(ev.timestamp_ns, 1_000_000_000)
      print(f"ts:{sec}.{nsec} falling edge - reset PLL chip")
      pll.reset()
