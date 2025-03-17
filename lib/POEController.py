
from smbus2 import SMBus

class POEController:

   REG_PORT_CLASS_DETECT_STATUS = 0x0C
   REG_PORT_MODE = 0x12
   REG_DETECT_CLASS_ENABLE = 0x14
   REG_TEMPERATURE = 0x2C
   REG_VPWR_LSB = 0x2E
   REG_PORT1_CURRENT_LSB = 0x30
   REG_PORT1_VOLTAGE_LSB = 0x32

   poe_class_str = [
      "unknown",
      "Class 1",
      "Class 2",
      "Class 3",
      "Class 4",
      "---",
      "Class 0",
      "overcurrent",
      "Class 5 4P Single Signature",
      "---",
      "---",
      "---",
      "Class 4 Type 1 Limited",
      "Class 5 Legacy",
      "---",
      "Class Mismatch"
   ]

   poe_detection_str = [
      "unknown",
      "short circuit",
      "capacitive",
      "RLOW",
      "RGOOD",
      "RHIGH",
      "open circuit",
      "PSE to PSE",
      "---",
      "---",
      "---",
      "---",
      "---",
      "---",
      "---",
      "mosfet fault"
   ]

   def __init__(self, i2c_bus, i2c_addr, i2c_select=()):
      self.i2c_addr = i2c_addr
      self.i2c_select = i2c_select
      self.bus = SMBus(i2c_bus)

   def select(self):
      for func in self.i2c_select:
         func()

   def read_register(self, reg_addr):
      self.select()
      return self.bus.read_byte_data(self.i2c_addr, reg_addr)

   def write_register(self, reg_addr, value):
      self.select()
      self.bus.write_byte_data(self.i2c_addr, reg_addr, value)
      
   def port_on(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      mask = 0x03 << (port * 2)
      regval = self.read_register(self.REG_PORT_MODE)
      regval |= mask
      self.write_register(self.REG_PORT_MODE, regval)
      self.write_register(self.REG_DETECT_CLASS_ENABLE, 0xFF)

   def port_off(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      mask = 0x03 << (port * 2)
      regval = self.read_register(self.REG_PORT_MODE)
      regval &= ~mask
      self.write_register(self.REG_PORT_MODE, regval)
      self.write_register(self.REG_DETECT_CLASS_ENABLE, 0xFF)

   def port_status(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      value = self.read_register(self.REG_PORT_MODE)
      return bool(value & (0x03 << (port * 2)))

   def port_voltage(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      addr = self.REG_PORT1_VOLTAGE_LSB + (port * 4)
      self.select()
      vlist = self.bus.read_i2c_block_data(self.i2c_addr, addr, 2)
      voltage = vlist[0] + (vlist[1] << 8)
      return round(float(60 * voltage / 16384.0), 2)

   def port_current(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      addr = self.REG_PORT1_CURRENT_LSB + (port * 4)
      self.select()
      clist = self.bus.read_i2c_block_data(self.i2c_addr, addr, 2)
      current = clist[0] + (clist[1] << 8)
      return round(float(1000 * current / 16384.0), 2)

   def port_power(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      return round(float(self.port_voltage(port) * self.port_current(port) / 1000.0), 2)

   def port_class(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      poeclass = (self.read_register(self.REG_PORT_CLASS_DETECT_STATUS + port) & (0xF0)) >> 4
      return self.poe_class_str[poeclass] 

   def port_detection(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      poedet = self.read_register(self.REG_PORT_CLASS_DETECT_STATUS + port) & (0x0F)
      return self.poe_detection_str[poedet] 

   def temperature(self):
      value = self.read_register(self.REG_TEMPERATURE)
      t = round(float((value * 0.652) - 20), 2)
      return t

   def voltage_in(self):
      self.select()
      value = self.bus.read_i2c_block_data(self.i2c_addr, self.REG_VPWR_LSB, 2)
      value = value[0] + (value[1] << 8)
      return round(float((value * 60) / 16384.0), 2)
