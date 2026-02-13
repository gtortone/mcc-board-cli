#!/usr/bin/env python3

import gpiod
import select

# input pin
IN_GPIO_BANK = 4
IN_GPIO_LINE = 46    # PLL_LOL PS_MIO46

# output pin
OUT_GPIO_BANK = 9
OUT_GPIO_LINE = 2    # PLL_LOCK 

# led pin
LED_GPIO_BANK = 3
LED_GPIO_LINE = 0

chip_in = gpiod.Chip(f"gpiochip{IN_GPIO_BANK}")
line_in = chip_in.get_line(IN_GPIO_LINE)

chip_out = gpiod.Chip(f"gpiochip{OUT_GPIO_BANK}")
line_out = chip_out.get_line(OUT_GPIO_LINE)

chip_led = gpiod.Chip(f"gpiochip{LED_GPIO_BANK}")
line_led = chip_led.get_line(LED_GPIO_LINE)

line_in.request(consumer="ps_pll_lol", type=gpiod.LINE_REQ_EV_BOTH_EDGES)  # rising + falling
line_out.request(consumer="pl_pll_lock", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])
line_led.request(consumer="ps_pll_led", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])

# init
line_out.set_value(line_in.get_value())
line_led.set_value(line_in.get_value())

poller = select.poll()
poller.register(line_in.event_get_fd(), select.POLLIN)

while True:

   poller.poll()

   ev = line_in.event_read()
   if ev.type == gpiod.LineEvent.RISING_EDGE:
      print(f"ts:{ev.sec}.{ev.nsec} rising edge")
   elif ev.type == gpiod.LineEvent.FALLING_EDGE:
      print(f"ts:{ev.sec}.{ev.nsec} falling edge")

   line_out.set_value(line_in.get_value())
   line_led.set_value(line_in.get_value())
