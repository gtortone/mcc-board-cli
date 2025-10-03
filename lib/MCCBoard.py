
from functools import partial

from lib.I2CSwitch import I2CSwitch
from lib.POEController import POEController
from lib.POESwitch import POESwitch
from lib.SFP import SFP
from lib.FPGARegister import FPGARegister

"""
I2C switch 0x72
   channel 0:     clock
   channel 1:     not used
   channel 2:     not used
   channel 3:     I2C switch 0x71

I2C switch 0x71
   channel 0:     poe
   channel 1:     sfp 1
   channel 2:     sfp 0
   channel 3:     not used

"""

class MCCBoard:

   I2C_BUS = 0
   I2C_SW0_ADDR = 0x71
   I2C_SW1_ADDR = 0x72
   I2C_POE0_ADDR = 0x20
   I2C_POE1_ADDR = 0x22
   I2C_SFP_ADDR = 0x50

   def __init__(self):
      isw1 = I2CSwitch(self.I2C_BUS, self.I2C_SW1_ADDR)
      isw2 = I2CSwitch(self.I2C_BUS, self.I2C_SW0_ADDR)
      
      self.sw = POESwitch()
      self.pc1 = POEController(self.I2C_BUS, self.I2C_POE0_ADDR, 
         (partial(isw1.select, 3), partial(isw2.select, 0)))
      self.pc2 = POEController(self.I2C_BUS, self.I2C_POE1_ADDR, 
         (partial(isw1.select, 3), partial(isw2.select, 0)))

      self.sw.add_controller(self.pc1)
      self.sw.add_controller(self.pc2)

      self.sfp0 = SFP(self.I2C_BUS, self.I2C_SFP_ADDR, 
         (partial(isw1.select, 3), partial(isw2.select, 2)))
      self.sfp1 = SFP(self.I2C_BUS, self.I2C_SFP_ADDR, 
         (partial(isw1.select, 3), partial(isw2.select, 1)))

      self.fpga = FPGARegister('/dev/uio0')
