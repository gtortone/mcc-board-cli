
import time
import gpiod
from gpiod.line import Direction, Value
from smbus2 import SMBus
from lib.gpiochip import open_chip

class I2CSwitch:

   selmap = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]

   def __init__(self, i2c_bus, i2c_addr, chip=None, line=None):
      self.i2c_addr = i2c_addr
      self.bus = SMBus(i2c_bus)
      if (chip is not None and line is not None):
         self.chip = open_chip(chip)
         self.pin = line
      else:
         self.chip = self.line = None

   def reset(self):
      if self.chip is not None:
         self.line = self.chip.request_lines(
            consumer="i2cmux_rst",
            config={self.pin: gpiod.LineSettings(direction=Direction.OUTPUT)})
         self.line.set_value(self.pin, Value.INACTIVE)
         time.sleep(0.1)
         self.line.set_value(self.pin, Value.ACTIVE)
         self.line.release()

   def select(self, channel):
      if channel not in range(8):
         raise IndexError("channel index must be inside [0...7] range")
      self.bus.write_byte_data(self.i2c_addr, 0x00, self.selmap[channel])

   def get_channel(self):
      return self.selmap.index(self.bus.read_byte_data(self.i2c_addr, 0x00))

