#!/usr/bin/env python3

import time
import gpiod
from gpiod.line import Direction, Edge, Value
import select
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.Si5345 import Si5345
from lib.gpiochip import open_chip

# input pin
IN_GPIO_BANK = "zynqmp_gpio"
IN_GPIO_LINE = 46    # PLL_LOL PS_MIO46

# output pin
OUT_GPIO_BANK = "a0130000.gpio"
OUT_GPIO_LINE = 2    # PLL_LOCK
GTXRST_GPIO_LINE = 3

# led pin
LED_GPIO_BANK = "a0060000.gpio"   # LED0
LED_GPIO_LINE = 0

chip_in = open_chip(f"{IN_GPIO_BANK}")
chip_out = open_chip(f"{OUT_GPIO_BANK}")
chip_led = open_chip(f"{LED_GPIO_BANK}")

# mirror PS_MIO46 to PL
# mirror PS_MIO46 to LED0
line_in = chip_in.request_lines(
   consumer="ps_pll_lol",
   config={IN_GPIO_LINE: gpiod.LineSettings(direction=Direction.INPUT,
                                            edge_detection=Edge.BOTH)})   # rising + falling
line_out = chip_out.request_lines(
   consumer="pl_pll_lock",
   config={OUT_GPIO_LINE: gpiod.LineSettings(direction=Direction.OUTPUT,
                                             output_value=Value.INACTIVE)})
line_led = chip_led.request_lines(
   consumer="ps_pll_led",
   config={LED_GPIO_LINE: gpiod.LineSettings(direction=Direction.OUTPUT,
                                             output_value=Value.INACTIVE)})
line_gtxrst = chip_out.request_lines(
   consumer="gtx_rst",
   config={GTXRST_GPIO_LINE: gpiod.LineSettings(direction=Direction.OUTPUT,
                                                output_value=Value.INACTIVE)})

# init
line_out.set_value(OUT_GPIO_LINE, line_in.get_value(IN_GPIO_LINE))
line_led.set_value(LED_GPIO_LINE, line_in.get_value(IN_GPIO_LINE))

# reset GTX
line_gtxrst.set_value(GTXRST_GPIO_LINE, Value.INACTIVE)
time.sleep(0.1)
line_gtxrst.set_value(GTXRST_GPIO_LINE, Value.ACTIVE)
time.sleep(0.1)
line_gtxrst.set_value(GTXRST_GPIO_LINE, Value.INACTIVE)

poller = select.poll()
poller.register(line_in.fd, select.POLLIN)

I2C_SI5342_BUS = 6
SI5342_I2C_ADDR = 0x68
pll = Si5345(I2C_SI5342_BUS, SI5342_I2C_ADDR)

while True:

   poller.poll()

   for ev in line_in.read_edge_events():
      sec, nsec = divmod(ev.timestamp_ns, 1_000_000_000)
      if ev.event_type == gpiod.EdgeEvent.Type.RISING_EDGE:
         print(f"ts:{sec}.{nsec} rising edge")
      elif ev.event_type == gpiod.EdgeEvent.Type.FALLING_EDGE:
         print(f"ts:{sec}.{nsec} falling edge")
         print("-- reset PLL")
         pll.reset()
         #time.sleep(2)

   line_out.set_value(OUT_GPIO_LINE, line_in.get_value(IN_GPIO_LINE))
   line_led.set_value(LED_GPIO_LINE, line_in.get_value(IN_GPIO_LINE))
