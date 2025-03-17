#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from functools import partial

from lib.MCCBoard import MCCBoard

mcc = MCCBoard()
print()

mcc.sw.print()
print()

print("SFP #0")
if mcc.sfp0.is_available():
   mcc.sfp0.print()
else:
   print("not available")
print()

print("SFP #1")
if mcc.sfp1.is_available():
   mcc.sfp1.print()
else:
   print("not available")
print()


