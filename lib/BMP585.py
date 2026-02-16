import time
from smbus2 import SMBus

class BMP585:

   REG_STATUS = 0x28
   REG_TEMP_DATA = 0x1D
   REG_PRESS_DATA = 0x20
   REG_CMD = 0x7E  
   RESET_CMD = 0xB6 
   
   REG_OSR = 0x36
   REG_ODR = 0x37
   REG_INT_SOURCE = 0x15

   def __init__(self, i2c_bus, i2c_addr, forced_mode=False, i2c_select=()):
      self.i2c_addr = i2c_addr
      self.i2c_select = i2c_select
      self.bus = SMBus(i2c_bus)
      self.forced_mode = forced_mode

      self.reset()

      if self.forced_mode:
         self.write_byte(self.REG_ODR, 0xF0)  # standby
      else:
         self.write_byte(self.REG_ODR, 0x81)  # normal - 240 kHz

      # enable data ready flag
      self.write_byte(self.REG_INT_SOURCE, 1)

      self.write_byte(self.REG_OSR, 0x64)  # oversampling x4 for T and P / enable pressure

   def select(self):
      for func in self.i2c_select:
         func()

   def reset(self):
      self.write_byte(self.REG_CMD, self.RESET_CMD)
      time.sleep(0.2)

   def read_byte(self, reg):
      self.select()
      return self.bus.read_byte_data(self.i2c_addr, reg)

   def read_bytes(self, reg, length):
      self.select()
      return self.bus.read_i2c_block_data(self.i2c_addr, reg, length)

   def write_byte(self, reg, value):
      self.select()
      self.bus.write_byte_data(self.i2c_addr, reg, value)

   def wait_for_data_ready(self, timeout=2.0):
      start = time.time()
      while True:
         status = self.read_byte(0x27)
         if (status & 0x01):
            return
         if (time.time() - start) > timeout:
            raise TimeoutError("Timeout waiting BMP585 readout")
         time.sleep(0.005)

   def trigger_forced_measurement(self):
      self.write_byte(self.REG_ODR, 0x82)  # start measurement
      time.sleep(0.002)

   def read_temperature(self):
      data = self.read_bytes(self.REG_TEMP_DATA, 3)
      raw = data[2] << 16 | data[1] << 8 | data[0]
      if raw & 0x800000:
         raw -= 1 << 24
      return raw / 65536.0

   def read_pressure(self):
      data = self.read_bytes(self.REG_PRESS_DATA, 3)
      raw = data[2] << 16 | data[1] << 8 | data[0]
      if raw & 0x800000:
         raw -= 1 << 24
      return raw / 64.0

   def read(self):
      if self.forced_mode:
         self.trigger_forced_measurement()
      self.wait_for_data_ready()
      temp = self.read_temperature()
      press = self.read_pressure()
      return (temp, press)

