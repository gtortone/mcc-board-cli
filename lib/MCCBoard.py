
from functools import partial

from lib.I2CSwitch import I2CSwitch
from lib.POEController import POEController
from lib.POESwitch import POESwitch
from lib.SFP import SFP
from lib.FPGADevice import FPGADevice
from lib.INA226 import INA226
from lib.INA238 import INA238
from lib.SHT40 import SHT40
from lib.BMP585 import BMP585

"""
======
MCCv2
======

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
"""

class MCCBoard:

   def __init__(self, ver):

      if ver == '1':
         None

      elif ver == '2':

         I2C_POE_BUS = 2
         I2C_POE0_ADDR = 0x20
         I2C_POE1_ADDR = 0x22

         I2C_SFP0_BUS = 3
         I2C_SFP1_BUS = 9
         I2C_SFP2_BUS = 8
         I2C_SFP_ADDR = 0x50

         I2C_SFP_MON_BUS = 4
         I2C_SFP0_MON_ADDR = 0x40
         I2C_SFP1_MON_ADDR = 0x41
         I2C_SFP2_MON_ADDR = 0x44

         I2C_BOARD_MON_BUS = 5
         I2C_56V_MON_ADDR = 0x40
         I2C_12V_MON_ADDR = 0x41

         I2C_ENV_MON_BUS = 7
         I2C_SHT40_ADDR = 0x44 
         I2C_BMP585_ADDR = 0x47

         self.sw = POESwitch()
         self.pc1 = POEController(I2C_POE_BUS, I2C_POE0_ADDR, (), portmap=[1, 0, 2, 3])
         self.pc2 = POEController(I2C_POE_BUS, I2C_POE1_ADDR, (), portmap=[1, 0, 2, 3])

         self.sw.add_controller(self.pc1)
         self.sw.add_controller(self.pc2)

         self.sfp = [
            SFP(I2C_SFP0_BUS, I2C_SFP_ADDR, (), "zynqmp_gpio", 49),
            SFP(I2C_SFP1_BUS, I2C_SFP_ADDR, (), "zynqmp_gpio", 48),
            SFP(I2C_SFP2_BUS, I2C_SFP_ADDR, (), "zynqmp_gpio", 47)
         ]

         self.sfpmon = [
            INA226(I2C_SFP_MON_BUS, I2C_SFP0_MON_ADDR, shunt_ohms=0.02),
            INA226(I2C_SFP_MON_BUS, I2C_SFP1_MON_ADDR, shunt_ohms=0.02),
            INA226(I2C_SFP_MON_BUS, I2C_SFP2_MON_ADDR, shunt_ohms=0.02)
         ]

         self.boardmon = [
            INA238(I2C_BOARD_MON_BUS, I2C_56V_MON_ADDR, shunt_ohms=0.02, max_current=10),
            INA226(I2C_BOARD_MON_BUS, I2C_12V_MON_ADDR, shunt_ohms=0.02),
         ]

         self.sht40 = SHT40(I2C_ENV_MON_BUS, I2C_SHT40_ADDR)

         self.bmp585 = BMP585(I2C_ENV_MON_BUS, I2C_BMP585_ADDR, forced_mode=True)

         self.fpga = FPGADevice('/dev/uio0')

      else:
         print(f"E: MCC version {ver} not valid")

