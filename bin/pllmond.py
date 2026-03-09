#!/usr/bin/env python3

import time
import gpiod
import select
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.Si5345 import Si5345

# input pin
IN_GPIO_BANK = "zynqmp_gpio" 
IN_GPIO_LINE = 46    # PLL_LOL PS_MIO46

# output pin
OUT_GPIO_BANK = "a0130000.gpio"
OUT_GPIO_LINE = 2    # PLL_LOCK 

# led pin
LED_GPIO_BANK = "a0060000.gpio"   # LED0
LED_GPIO_LINE = 0

chip_in = gpiod.Chip(f"{IN_GPIO_BANK}")
line_in = chip_in.get_line(IN_GPIO_LINE)

chip_out = gpiod.Chip(f"{OUT_GPIO_BANK}")
line_out = chip_out.get_line(OUT_GPIO_LINE)

chip_led = gpiod.Chip(f"{LED_GPIO_BANK}")
line_led = chip_led.get_line(LED_GPIO_LINE)

# mirror PS_MIO46 to PL
# mirror PS_MIO46 to LED0
line_in.request(consumer="ps_pll_lol", type=gpiod.LINE_REQ_EV_BOTH_EDGES)  # rising + falling
line_out.request(consumer="pl_pll_lock", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
line_led.request(consumer="ps_pll_led", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])

# init
line_out.set_value(line_in.get_value())
line_led.set_value(line_in.get_value())

poller = select.poll()
poller.register(line_in.event_get_fd(), select.POLLIN)

I2C_SI5342_BUS = 6
SI5342_I2C_ADDR = 0x68
pll = Si5345(I2C_SI5342_BUS, SI5342_I2C_ADDR)

while True:

   poller.poll()

   ev = line_in.event_read()
   if ev.type == gpiod.LineEvent.RISING_EDGE:
      print(f"ts:{ev.sec}.{ev.nsec} rising edge")
   elif ev.type == gpiod.LineEvent.FALLING_EDGE:
      print(f"ts:{ev.sec}.{ev.nsec} falling edge")
      print("-- reset PLL")
      pll.reset()
      #time.sleep(2)

   line_out.set_value(line_in.get_value())
   line_led.set_value(line_in.get_value())
