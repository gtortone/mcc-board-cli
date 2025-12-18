
from functools import partial

from lib.I2CSwitch import I2CSwitch
from lib.POEController import POEController
from lib.POESwitch import POESwitch
from lib.SFP import SFP
from lib.FPGARegister import FPGARegister

"""
I2C switch 0x70
---------------
channel 0:        Si3472      (POE0)         addr: 0x20
                  Si3472      (POE1)         addr: 0x22

channel 1:        SFP0                       addr: 0x50

channel 2:        INA226      (SFP0)         addr: 0x40
                  INA226      (SFP1)         addr: 0x41
                  INA226      (SFP2)         addr: 0x44

channel 3:        INA238      (56V)          addr: 0x40
                  INA226      (12V)          addr: 0x41

channel 4:        Si5345A     (PLL)          addr: 0x68

channel 5:        BMP585      (pressure)     addr: 0x47
                  SHT40       (T/H)          addr: 0x44

channel 6:        SFP2                       addr: 0x50

channel 7:        SFP1                       addr: 0x50

GPIO layout
-----------
SFP0 power switch:       SFP0_EN        (AP22653AW6-7 switch)      PS_MIO49
SFP0 fault:              SFP0_FAULT     (AP22653AW6-7 switch)
SFP0 alert:              SFP0_ALERT     (INA226)

SFP1 power switch:       SFP1_EN        (AP22653AW6-7 switch)      PS_MIO48
SFP1 fault:              SFP1_FAULT     (AP22653AW6-7 switch)
SFP0 alert:              SFP0_ALERT     (INA226)

SFP2 power switch:       SFP2_EN        (AP22653AW6-7 switch)      PS_MIO47
SFP2 fault:              SFP2_FAULT     (AP22653AW6-7 switch)
SFP2 alert:              SFP2_ALERT     (INA226)

ALERT56                                 (INA238)                   PS_MIO50
ALERT12:                                (INA226)                   PS_MIO51
"""

class MCCBoard:

   I2C_BUS = 0
   I2C_SW_ADDR = 0x70
   I2C_POE0_ADDR = 0x20
   I2C_POE1_ADDR = 0x22
   I2C_SFP_ADDR = 0x50

   def __init__(self):
      isw = I2CSwitch(self.I2C_BUS, self.I2C_SW_ADDR, "gpiochip3", 0)
      isw.reset()
      
      self.sw = POESwitch()
      self.pc1 = POEController(self.I2C_BUS, self.I2C_POE0_ADDR, 
         (partial(isw.select, 0),), portmap=[1, 0, 2, 3])
      self.pc2 = POEController(self.I2C_BUS, self.I2C_POE1_ADDR, 
         (partial(isw.select, 0),), portmap=[1, 0, 2, 3])

      self.sw.add_controller(self.pc1)
      self.sw.add_controller(self.pc2)

      self.sfp = [
            SFP(self.I2C_BUS, self.I2C_SFP_ADDR, 
               (partial(isw.select, 1),), "gpiochip7", 49),
            SFP(self.I2C_BUS, self.I2C_SFP_ADDR, 
               (partial(isw.select, 7),), "gpiochip7", 48),
            SFP(self.I2C_BUS, self.I2C_SFP_ADDR, 
               (partial(isw.select, 6),), "gpiochip7", 47)
      ]

      self.fpga = FPGARegister('/dev/uio0')

