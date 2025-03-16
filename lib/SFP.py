
from smbus2 import SMBus

class SFP:

   REG_VENDOR = 0x14
   REG_MODEL = 0x28
   REG_SERIAL = 0x44
   REG_DATECODE = 0x54
   REG_TEMPERATURE = 0x60
   REG_VCC = 0x62
   REG_TXBIAS = 0x64
   REG_TXPOWER = 0x66
   REG_RXPOWER = 0x68

   def __init__(self, i2c_bus, i2c_addr):
      self.i2c_addr = i2c_addr
      self.bus = SMBus(i2c_bus)

   def is_available(self):
      try:
         self.bus.read_byte_data(self.i2c_addr, 0x00)
      except:
         return False
      return True

   def vendor(self):
      vendor = self.bus.read_i2c_block_data(self.i2c_addr, self.REG_VENDOR, 16)
      return str.rstrip(''.join(map(chr, vendor)))

   def model(self):
      model = self.bus.read_i2c_block_data(self.i2c_addr, self.REG_MODEL, 20)
      return str.rstrip(''.join(map(chr, model)))

   def serial(self):
      serial = self.bus.read_i2c_block_data(self.i2c_addr, self.REG_SERIAL, 16)
      return str.rstrip(''.join(map(chr, serial)))

   def datecode(self):
      datecode = self.bus.read_i2c_block_data(self.i2c_addr, self.REG_DATECODE, 8)
      return str.rstrip(''.join(map(chr, datecode)))

   def temperature(self):
      tlist = self.bus.read_i2c_block_data(self.i2c_addr+1, self.REG_TEMPERATURE, 2)
      temp = (tlist[0] << 8) + tlist[1]
      return round(float(temp * 1/256), 2)   # LSB = 1/256 C
      
   def voltage(self):
      vlist = self.bus.read_i2c_block_data(self.i2c_addr+1, self.REG_VCC, 2)
      voltage = (vlist[0] << 8) + vlist[1]
      return round(float(voltage * 1E-4), 2)  # LSB = 100 uV

   def tx_bias(self):
      blist = self.bus.read_i2c_block_data(self.i2c_addr+1, self.REG_TXBIAS, 2)
      bias = (blist[0] << 8) + blist[1]
      return round(float(bias * 2)/1000.0, 2)  # LSB = 2 uA

   def tx_power(self):
      plist = self.bus.read_i2c_block_data(self.i2c_addr+1, self.REG_TXPOWER, 2)
      power = (plist[0] << 8) + plist[1]
      return round(float(power * 0.1), 2)  # LSB = 0.1 uW

   def rx_power(self):
      plist = self.bus.read_i2c_block_data(self.i2c_addr+1, self.REG_RXPOWER, 2)
      power = (plist[0] << 8) + plist[1]
      return round(float(power * 0.1), 2)  # LSB = 0.1 uW
