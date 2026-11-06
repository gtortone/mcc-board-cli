#!/usr/bin/env python3

import gpiod
from gpiod.line import Direction, Value
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.gpiochip import open_chip

# reset pin
OUT_GPIO_BANK = "a0130000.gpio"
OUT_GPIO_LINE = 3    # Timing reset

chip_out = open_chip(f"{OUT_GPIO_BANK}")

line_out = chip_out.request_lines(
   consumer="pl_timing_rst",
   config={OUT_GPIO_LINE: gpiod.LineSettings(direction=Direction.OUTPUT,
                                             output_value=Value.INACTIVE)})

# reset
line_out.set_value(OUT_GPIO_LINE, Value.ACTIVE)
time.sleep(0.1)
line_out.set_value(OUT_GPIO_LINE, Value.INACTIVE)

print("Timing reset: done")
