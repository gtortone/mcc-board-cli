
from smbus2 import SMBus

class I2CSwitch:

   selmap = [0x1, 0x2, 0x4, 0x8]

   def __init__(self, i2c_bus, i2c_addr):
      self.i2c_addr = i2c_addr
      self.bus = SMBus(i2c_bus)

   def select(self, channel):
      if channel not in range(4):
         raise IndexError("channel index must be inside [0...3] range")
      self.bus.write_byte_data(self.i2c_addr, 0x00, self.selmap[channel])

   def get_channel(self):
      return self.selmap.index(self.bus.read_byte_data(self.i2c_addr, 0x00))

