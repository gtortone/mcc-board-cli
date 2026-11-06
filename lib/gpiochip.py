
import glob
import os
import gpiod

def find_chip_path(name):
   """
   Resolve a GPIO chip character device path (libgpiod v2 only accepts paths).

   'name' can be:
     - a full path         ("/dev/gpiochip0")
     - a chip name         ("gpiochip0")
     - a chip number       ("0")
     - a chip label        ("a0130000.gpio", "zynqmp_gpio")
   """
   name = str(name)

   if os.path.isabs(name) and gpiod.is_gpiochip_device(name):
      return name

   if name.isdigit():
      candidate = f"/dev/gpiochip{name}"
   else:
      candidate = os.path.join("/dev", name)
   if gpiod.is_gpiochip_device(candidate):
      return candidate

   # lookup by label
   for path in sorted(glob.glob("/dev/gpiochip*")):
      if not gpiod.is_gpiochip_device(path):
         continue
      with gpiod.Chip(path) as chip:
         if chip.get_info().label == name:
            return path

   raise FileNotFoundError(f"GPIO chip '{name}' not found")

def open_chip(name):
   """Open a GPIO chip by path, name, number or label."""
   return gpiod.Chip(find_chip_path(name))
