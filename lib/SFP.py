
from smbus2 import SMBus

class SFP:

   REG_CONNECTOR_TYPE = 0x02
   REG_VENDOR = 0x14
   REG_MODEL = 0x28
   REG_SERIAL = 0x44
   REG_DATECODE = 0x54
   REG_TEMPERATURE = 0x60
   REG_VCC = 0x62
   REG_TXBIAS = 0x64
   REG_TXPOWER = 0x66
   REG_RXPOWER = 0x68

   LC_CONNECTOR_TYPE = 0x07

   def __init__(self, i2c_bus, i2c_addr, i2c_select=()):
      self.i2c_addr = i2c_addr
      self.i2c_select = i2c_select
      self.bus = SMBus(i2c_bus)

   def select(self):
      for func in self.i2c_select:
         func()

   def is_available(self):
      self.select()
      try:
         self.bus.read_byte_data(self.i2c_addr, 0x00)
      except:
         return False
      return True

   def connector_type(self):
      self.select() 
      conn = self.bus.read_i2c_block_data(self.i2c_addr, self.REG_CONNECTOR_TYPE, 1);
      return conn[0]

   def vendor(self):
      self.select()
      vendor = self.bus.read_i2c_block_data(self.i2c_addr, self.REG_VENDOR, 16)
      return str.rstrip(''.join(map(chr, vendor)))

   def model(self):
      self.select()
      model = self.bus.read_i2c_block_data(self.i2c_addr, self.REG_MODEL, 20)
      return str.rstrip(''.join(map(chr, model)))

   def serial(self):
      self.select()
      serial = self.bus.read_i2c_block_data(self.i2c_addr, self.REG_SERIAL, 16)
      return str.rstrip(''.join(map(chr, serial)))

   def datecode(self):
      self.select()
      datecode = self.bus.read_i2c_block_data(self.i2c_addr, self.REG_DATECODE, 8)
      return str.rstrip(''.join(map(chr, datecode)))

   def temperature(self):
      self.select()
      try:
         tlist = self.bus.read_i2c_block_data(self.i2c_addr+1, self.REG_TEMPERATURE, 2)
      except:
         return None
      temp = (tlist[0] << 8) + tlist[1]
      return round(float(temp * 1/256), 2)   # LSB = 1/256 C
      
   def voltage(self):
      self.select()
      try:
         vlist = self.bus.read_i2c_block_data(self.i2c_addr+1, self.REG_VCC, 2)
      except:
         return None
      voltage = (vlist[0] << 8) + vlist[1]
      return round(float(voltage * 1E-4), 2)  # LSB = 100 uV

   def tx_bias(self):
      self.select()
      try:
         blist = self.bus.read_i2c_block_data(self.i2c_addr+1, self.REG_TXBIAS, 2)
      except:
         return None
      bias = (blist[0] << 8) + blist[1]
      return round(float(bias * 2)/1000.0, 2)  # LSB = 2 uA

   def tx_power(self):
      self.select()
      try:
         plist = self.bus.read_i2c_block_data(self.i2c_addr+1, self.REG_TXPOWER, 2)
      except:
         return None
      power = (plist[0] << 8) + plist[1]
      return round(float(power * 0.1), 2)  # LSB = 0.1 uW

   def rx_power(self):
      self.select()
      try:
         plist = self.bus.read_i2c_block_data(self.i2c_addr+1, self.REG_RXPOWER, 2)
      except: 
         return None
      power = (plist[0] << 8) + plist[1]
      return round(float(power * 0.1), 2)  # LSB = 0.1 uW

   def print(self):
      print(f"vendor: {self.vendor()}")
      print(f"model: {self.model()}")
      print(f"serial: {self.serial()}")
      print(f"datecode: {self.datecode()}")
      if(self.connector_type() == self.LC_CONNECTOR_TYPE):
         print(f"voltage: {self.voltage()}V")
         print(f"temperature: {self.temperature()}C")
         print(f"tx bias: {self.tx_bias()}mA")
         print(f"tx power: {self.tx_power()}uW")
         print(f"rx power: {self.rx_power()}uW")

   def as_dict(self):
      d = {}
      d["vendor"] = self.vendor()
      d["model"] = self.model()
      d["serial"] = self.serial()
      d["datecode"] = self.datecode()
      if(self.connector_type() == self.LC_CONNECTOR_TYPE):
         d["voltage"] = self.voltage()
         d["temperature"] = self.temperature()
         d["tx bias"] = self.tx_bias()
         d["tx power"] = self.tx_power()
         d["rx power"] = self.rx_power()

      return d
