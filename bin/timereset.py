#!/usr/bin/env python3

import gpiod
import time

# reset pin
OUT_GPIO_BANK = "a0130000.gpio"
OUT_GPIO_LINE = 3    # Timing reset

chip_out = gpiod.Chip(f"{OUT_GPIO_BANK}")
line_out = chip_out.get_line(OUT_GPIO_LINE)

line_out.request(consumer="pl_timing_rst", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])

# reset 
line_out.set_value(1)
time.sleep(0.1)
line_out.set_value(0)

print("Timing reset: done")
