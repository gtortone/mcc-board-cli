#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from time import sleep

from lib.SHT40 import SHT40

if __name__ == "__main__":

   sht40 = SHT40(7, 0x44)

   while True:
      print(sht40.read())
      print("===================================================")
      sleep(0.2)
