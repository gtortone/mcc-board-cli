
class POESwitch:

   poectrl = []

   def __init__(self):
      pass

   def add_controller(self, ctrl):
      self.poectrl.append(ctrl) 

   def port_on(self, index):
      if index not in range(4 * len(self.poectrl)):
         raise IndexError(f"port index must be inside [0...{4*len(self.poectrl)}] range")
      self.poectrl[int(index/4)].port_on(index%4)

   def port_off(self, index):
      if index not in range(4 * len(self.poectrl)):
         raise IndexError(f"port index must be inside [0...{4*len(self.poectrl)}] range")
      self.poectrl[int(index/4)].port_off(index%4)

   def port_status(self, index):
      if index not in range(4 * len(self.poectrl)):
         raise IndexError(f"port index must be inside [0...{4*len(self.poectrl)}] range")
      return self.poectrl[int(index/4)].port_status(index%4)

   def port_voltage(self, index):
      if index not in range(4 * len(self.poectrl)):
         raise IndexError(f"port index must be inside [0...{4*len(self.poectrl)}] range")
      return self.poectrl[int(index/4)].port_voltage(index%4)

   def port_current(self, index):
      if index not in range(4 * len(self.poectrl)):
         raise IndexError(f"port index must be inside [0...{4*len(self.poectrl)}] range")
      return self.poectrl[int(index/4)].port_current(index%4)

   def port_power(self, index):
      if index not in range(4 * len(self.poectrl)):
         raise IndexError(f"port index must be inside [0...{4*len(self.poectrl)}] range")
      return self.poectrl[int(index/4)].port_power(index%4)

   def port_class(self, index):
      if index not in range(4 * len(self.poectrl)):
         raise IndexError(f"port index must be inside [0...{4*len(self.poectrl)}] range")
      return self.poectrl[int(index/4)].port_class(index%4)

   def port_detection(self, index):
      if index not in range(4 * len(self.poectrl)):
         raise IndexError(f"port index must be inside [0...{4*len(self.poectrl)}] range")
      return self.poectrl[int(index/4)].port_detection(index%4)
   
   def voltage_in(self, index):
      if index not in range(len(self.poectrl)):
         raise IndexError(f"controller index must inside [0...{len(self.poectrl)}] range")
      return self.poectrl[int(index/4)].voltage_in()

   def temperature(self, index):
      if index not in range(len(self.poectrl)):
         raise IndexError(f"controller index must inside [0...{len(self.poectrl)}] range")
      return self.poectrl[int(index/4)].temperature()

   def print(self):
      i = 0
      for ctrl in self.poectrl:
         print(f"POE ctrl: {i:2>}\tvoltage: {ctrl.voltage_in():5}V\t temperature: {ctrl.temperature():5}C")
         for port in range(4*i,(4*i)+4):
            s = f"\tport: {port}\t {'ON' if self.port_status(port) else 'OFF':>3} | " + \
               f"class: {self.port_class(port)} | " + \
               f"detection: {self.port_detection(port)}\n" + \
               f"\t\tvoltage: {self.port_voltage(port):5}V | " + \
               f"current: {self.port_current(port):5}mA | " + \
               f"power: {self.port_power(port):5}W"
            print(f"{s}\n")
         i += 1

   def as_dict(self, index):
      c = int(index/4)
      p = index % 4
      d = {}
      d["id"] = index
      d["status"] = 'on' if self.poectrl[c].port_status(p) else 'off'
      d["class"] = self.poectrl[c].port_class(p)
      d["detection"] = self.poectrl[c].port_detection(p)
      d["voltage"] = self.poectrl[c].port_voltage(p)
      d["current"] = self.poectrl[c].port_current(p)
      d["power"] = self.poectrl[c].port_power(p)

      return d
      
