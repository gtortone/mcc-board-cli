
import time
import gpiod
from smbus2 import SMBus

class I2CSwitch:

   selmap = [0x1, 0x2, 0x4, 0x8, 0x10, 0x20, 0x40, 0x80]

   def __init__(self, i2c_bus, i2c_addr, chip=None, line=None):
      self.i2c_addr = i2c_addr
      self.bus = SMBus(i2c_bus)
      if (chip is not None and line is not None):
         self.chip = gpiod.Chip(chip)
         self.pin = line
      else:
         self.chip = self.line = None

   def reset(self):
      if self.chip is not None:
         self.line = self.chip.get_line(self.pin)
         self.line.request(consumer="i2cmux_rst", type=gpiod.LINE_REQ_DIR_OUT)
         self.line.set_value(0)
         time.sleep(0.1)
         self.line.set_value(1)
         self.line.release()

   def select(self, channel):
      if channel not in range(8):
         raise IndexError("channel index must be inside [0...7] range")
      self.bus.write_byte_data(self.i2c_addr, 0x00, self.selmap[channel])

   def get_channel(self):
      return self.selmap.index(self.bus.read_byte_data(self.i2c_addr, 0x00))

