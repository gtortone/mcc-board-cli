
import time
from smbus2 import SMBus

class INA238:

   REG_CONFIG          = 0x00
   REG_ADC_CONFIG      = 0x01
   REG_SHUNT_CAL       = 0x02
   REG_SHUNT_TEMPCO    = 0x03
   REG_VSHUNT          = 0x04
   REG_VBUS            = 0x05
   REG_DIETEMP         = 0x06
   REG_CURRENT         = 0x07
   REG_POWER           = 0x08
   REG_DIAG_ALERT      = 0x0B
   REG_MANUFACTURER_ID = 0x3E
   REG_DEVICE_ID       = 0x3F

   def __init__(self, i2c_bus, i2c_addr, shunt_ohms=0.02, max_current=10, i2c_select=()):
      self.i2c_addr = i2c_addr
      self.i2c_select = i2c_select
      self.bus = SMBus(i2c_bus)
   
      self.shunt_ohms = shunt_ohms
      self.max_current = max_current
      self.current_lsb = max_current / 32768.0
      self.select() 

      self.configure()
      self.calibrate()

   def select(self):
      for func in self.i2c_select:
         func()

   def read_register_16(self, reg):
      self.select()
      data = self.bus.read_i2c_block_data(self.i2c_addr, reg, 2)
      return (data[0] << 8) | data[1]

   def read_register_24(self, reg):
      self.select()
      data = self.bus.read_i2c_block_data(self.i2c_addr, reg, 3)
      return (data[0] << 16) | (data[1] << 8) | data[0]

   def write_register(self, reg, value):
      data = [(value >> 8) & 0xFF, value & 0xFF]
      self.select()
      self.bus.write_i2c_block_data(self.i2c_addr, reg, data)

   def read_signed(self, reg):
      self.select()
      value = self.read_register_16(reg)
      if value & 0x8000:
         value -= 1 << 16
      return value

   def calibrate(self):
      cal = int(819.2e6 * self.current_lsb * self.shunt_ohms)  # ADCRANGE = 0
      #cal = int(819.2e6 * self.current_lsb * self.shunt_ohms) * 4    # ADCRANGE = 1
      self.write_register(self.REG_SHUNT_CAL, cal)

   def configure(self):
      # reset
      self.write_register(self.REG_CONFIG, 0x8000)
      time.sleep(0.2)
   
   def voltage(self):
      return self.read_register_16(self.REG_VBUS) * 3.125e-3  # 3.125 mV/bit     

   def supply_voltage(self):
      return float(self.voltage()) + (float(self.shunt_voltage()) / 1000)

   def shunt_voltage(self):
      return self.read_register_16(self.REG_VSHUNT) * 5e-6 * 1000 # 5 uV/bit  - ADCRANGE = 0
      #return self.read_register)16(self.REG_VSHUNT) * 1.25e-6  # 1.25 uV/bit  - ADCRANGE = 1

   def current(self):
      return self.read_register_16(self.REG_CURRENT) * self.current_lsb

   def power(self):
      return 0.2 * self.read_register_24(self.REG_POWER) * self.current_lsb
       
   def die_temperature(self):
      return self.read_register_16(self.REG_DIETEMP) * 0.125  # 0.125 °C/bit
      
