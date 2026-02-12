
from smbus2 import SMBus

class Si5345:

   REG_PAGE_SELECT = 0x0001
   REG_RESET = 0x001C

   def __init__(self, i2c_bus, i2c_addr, i2c_select=()):
      self.i2c_addr = i2c_addr
      self.i2c_select = i2c_select
      self.bus = SMBus(i2c_bus)

      self.select()

   def select(self):
      for func in self.i2c_select:
         func()

   def set_page(self, address):
      page = (address >> 8) & 0xFF
      self.bus.write_byte_data(self.i2c_addr, self.REG_PAGE_SELECT, page)

   def read_register(self, reg_addr):
      self.select()
      self.set_page(reg_addr)
      return self.bus.read_byte_data(self.i2c_addr, reg_addr)

   def write_register(self, reg_addr, value):
      self.select()
      self.set_page(reg_addr)
      self.bus.write_byte_data(self.i2c_addr, reg_addr, value)

   def reset(self):
      self.write_register(self.REG_RESET, 1)

