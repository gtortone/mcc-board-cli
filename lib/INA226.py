
from math import trunc
from smbus2 import SMBus

class INA226:
   
   AVG_1BIT = 0  # 1 samples at 16-bit
   AVG_4BIT = 1
   AVG_16BIT = 2
   AVG_64BIT = 3
   AVG_128BIT = 4
   AVG_256BIT = 5
   AVG_512BIT = 6
   AVG_1024BIT = 7

   VCT_140us_BIT = 0
   VCT_204us_BIT = 1
   VCT_332us_BIT = 2
   VCT_588us_BIT = 3
   VCT_1100us_BIT = 4
   VCT_2116us_BIT = 5
   VCT_4156us_BIT = 6
   VCT_8244us_BIT = 7

   REG_CONFIG = 0x00
   REG_SHUNTVOLTAGE = 0x01
   REG_BUSVOLTAGE = 0x02
   REG_POWER = 0x03
   REG_CURRENT = 0x04
   REG_CALI = 0x05
   REG_MASK = 0x06
   REG_LIMIT = 0x07
   REG_MANUFACTURER_ID = 0XFE
   REG_DIE_ID = 0XFF

   FLAG_RST = 15
   FLAG_AVG0 = 9
   FLAG_CONT_SH_BUS = 7
   FLAG_VBUSCT0 = 6
   FLAG_VSHCT0 = 3
   FLAG_MODE3 = 2
   FLAG_MODE2 = 1
   FLAG_MODE1 = 0
   FLAG_CVRF = 3
   FLAG_OVF = 2

   BUS_RANGE = 40.96  # HEX = 7FFF, LSB = 1.25 mV, Must to positive
   GAIN_VOLTS = 0.08192  # HEX = 7FFF, LSB = 2.5 uV, An MSB = '1' denotes a negative number.
   SHUNT_MILLIVOLTS_LSB = 0.0025
   BUS_MILLIVOLTS_LSB = 1.25
   CALIBRATION_FACTOR = 0.00512
   MAX_CALIBRATION_VALUE = 0x7FFF  # Max value supported (32767 decimal)
   MAX_CURRENT_VALUE = 0x7FFF
   CURRENT_LSB_FACTOR = 32768

   def __init__(self, i2c_bus, i2c_addr, shunt_ohms=0.02, i2c_select=()):
      self.i2c_addr = i2c_addr
      self.i2c_select = i2c_select
      self.bus = SMBus(i2c_bus)
   
      self.shunt_ohms = shunt_ohms
      self.min_device_current_lsb = self.CALIBRATION_FACTOR / (self.shunt_ohms * self.MAX_CALIBRATION_VALUE)
      self.max_expected_amps = None

      self.configure(avg_mode=INA226.AVG_16BIT)
      self.select() 

   def select(self):
      for func in self.i2c_select:
         func()

   def configure(self, avg_mode=AVG_1BIT, bus_ct=VCT_8244us_BIT, shunt_ct=VCT_8244us_BIT):
      self.calibrate(self.BUS_RANGE, self.GAIN_VOLTS, self.max_expected_amps)
      configuration = (avg_mode << self.FLAG_AVG0 | bus_ct << self.FLAG_VBUSCT0 | shunt_ct << self.FLAG_VSHCT0 | 
         self.FLAG_CONT_SH_BUS | 1 << 14)
      self.write_register(self.REG_CONFIG, configuration)

   def calibrate(self, bus_volts_max, shunt_volts_max, max_expected_amps=None):
      max_possible_amps = shunt_volts_max / self.shunt_ohms
      self.current_lsb = self.determine_current_lsb(max_expected_amps, max_possible_amps)
      self.power_lsb = self.current_lsb * 25.2
      max_current = self.current_lsb * self.MAX_CURRENT_VALUE
      max_shunt_voltage = max_current * self.shunt_ohms
      calibration = trunc(self.CALIBRATION_FACTOR / (self.current_lsb * self.shunt_ohms))
      self.write_register(self.REG_CALI, calibration)

   def determine_current_lsb(self, max_expected_amps, max_possible_amps):
      if max_expected_amps is not None:
         if max_expected_amps > round(max_possible_amps, 3):
            raise ValueError
         if max_expected_amps < max_possible_amps:
            current_lsb = max_expected_amps / self.CURRENT_LSB_FACTOR
         else:
            current_lsb = max_possible_amps / self.CURRENT_LSB_FACTOR
      else:
         current_lsb = max_possible_amps / self.CURRENT_LSB_FACTOR
      if current_lsb < self.min_device_current_lsb:
         current_lsb = self.min_device_current_lsb
      return current_lsb

   def has_current_overflow(self):
      return self.read_register(self.REG_MASK) >> self.FLAG_OVF & 1

   def is_conversion_ready(self):
      return self.read_register(self.REG_MASK) >> self.FLAG_CVRF & 1

   def voltage(self):
      return float(self.read_register(self.REG_BUSVOLTAGE)) * self.BUS_MILLIVOLTS_LSB / 1000

   def supply_voltage(self):
      return float(self.voltage()) + (float(self.shunt_voltage()) / 1000)

   def shunt_voltage(self):
      return self.read_register(self.REG_SHUNTVOLTAGE, True) * self.SHUNT_MILLIVOLTS_LSB

   def current(self):
      return self.read_register(self.REG_CURRENT, True) * self.current_lsb

   def power(self):
      return self.read_register(self.REG_POWER) * self.power_lsb

   def write_register(self, register, register_value):
      register_bytes = [(register_value >> 8) & 0xFF, register_value & 0xFF]
      self.select()
      self.bus.write_i2c_block_data(self.i2c_addr, register, register_bytes)

   def read_register(self, register, negative_value_supported=False):
      self.select()
      result = self.bus.read_word_data(self.i2c_addr, register) & 0xFFFF
      register_value = ((result << 8) & 0xFF00) + (result >> 8)
      if negative_value_supported:
         if register_value > 32767:
            register_value -= 65536
      return register_value

    
