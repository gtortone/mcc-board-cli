
import gpiod
import time
from smbus2 import SMBus

class POEController:

   REG_PORT_CLASS_DETECT_STATUS = 0x0C
   REG_PORT_MODE = 0x12
   REG_DISCONNECT_ENABLE = 0x13
   REG_DETECT_CLASS_ENABLE = 0x14
   REG_PORT_REMAP = 0x26
   REG_TEMPERATURE = 0x2C
   REG_VPWR_LSB = 0x2E
   REG_PORT1_CURRENT_LSB = 0x30
   REG_PORT1_VOLTAGE_LSB = 0x32
   REG_PB_POWER_ENABLE = 0x19
   REG_PB_RESET = 0x1A
   REG_VENDOR_ID = 0x1B

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

   def __init__(self, i2c_bus, i2c_addr, i2c_select=(), chip_sw=None, line_sw=None, portmap=[]):
      self.i2c_addr = i2c_addr
      self.i2c_select = i2c_select
      self.bus = SMBus(i2c_bus)
      if len(portmap) == 0:
         self.portmap = [0, 1, 2, 3]
      else:
         self.portmap = portmap

      if (chip_sw is not None and line_sw is not None):
         self.chip_sw = gpiod.Chip(chip_sw)
         self.line_sw = line_sw
      else:
         self.chip_sw = self.line_sw = None

      self.select()

      # release reset and power off POE lines
      #if self.chip_sw is not None:
      #   line = self.chip_sw.get_line(self.line_sw)
      #   line.request(consumer="poe_rst", type=gpiod.LINE_REQ_DIR_AS_IS)
      #   if line.get_value() == 0:
      #      start = time.time()
      #      line.set_value(1)

      #      while (time.time() - start) < 1:
      #         try:
      #            self.write_register(self.REG_PORT_MODE, 0x00)
      #            time.sleep(0.05)
      #         except:
      #            pass

      #   line.release()

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
      mask = 0x03 << (self.portmap.index(port) * 2)
      regval = self.read_register(self.REG_PORT_MODE)
      regval |= mask
      self.write_register(self.REG_PORT_MODE, regval)
      self.write_register(self.REG_DETECT_CLASS_ENABLE, 0xFF)

   def port_off(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      mask = 0x03 << (self.portmap.index(port) * 2)
      regval = self.read_register(self.REG_PORT_MODE)
      regval &= ~mask
      self.write_register(self.REG_PORT_MODE, regval)
      self.write_register(self.REG_DETECT_CLASS_ENABLE, 0xFF)

   def port_status(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      value = self.read_register(self.REG_PORT_MODE)
      return bool(value & (0x03 << (self.portmap.index(port) * 2)))

   def port_voltage(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      addr = self.REG_PORT1_VOLTAGE_LSB + (self.portmap.index(port) * 4)
      self.select()
      vlist = self.bus.read_i2c_block_data(self.i2c_addr, addr, 2)
      voltage = vlist[0] + (vlist[1] << 8)
      return round(float(60 * voltage / 16384.0), 2)

   def port_current(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      addr = self.REG_PORT1_CURRENT_LSB + (self.portmap.index(port) * 4)
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
      poeclass = (self.read_register(self.REG_PORT_CLASS_DETECT_STATUS + self.portmap.index(port)) & (0xF0)) >> 4
      return self.poe_class_str[poeclass] 

   def port_detection(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      poedet = self.read_register(self.REG_PORT_CLASS_DETECT_STATUS + self.portmap.index(port)) & (0x0F)
      return self.poe_detection_str[poedet] 

   def port_set_keep_power(self, port, value):
      # keep port power even if PD current too low
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      mask = 0x01 << self.portmap.index(port)
      regval = self.read_register(self.REG_DISCONNECT_ENABLE)

      if not value:
         regval |= mask
      else:
         regval &= ~mask;
         
      self.write_register(self.REG_DISCONNECT_ENABLE, regval)

   def port_get_keep_power(self, port):
      if port not in range(4):
         raise IndexError("port index must be inside [0...3] range")
      return not bool(self.read_register(self.REG_DISCONNECT_ENABLE) & (1 << self.portmap.index(port)))

   def temperature(self):
      value = self.read_register(self.REG_TEMPERATURE)
      t = round(float((value * 0.652) - 20), 2)
      return t

   def voltage_in(self):
      self.select()
      value = self.bus.read_i2c_block_data(self.i2c_addr, self.REG_VPWR_LSB, 2)
      value = value[0] + (value[1] << 8)
      return round(float((value * 60) / 16384.0), 2)

   def as_dict(self):
      d = {}
      d["voltage"] = self.voltage_in()
      d["temperature"] = self.temperature()
      
      return d
