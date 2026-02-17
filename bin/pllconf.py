#!/usr/bin/env python3

import argparse
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.I2CSwitch import I2CSwitch
from lib.Si5345 import Si5345
from functools import partial

I2C_BUS = 0

SI5342_I2C_BUS = 6
SI5342_I2C_ADDR = 0x68

reserved_regs = [0x001C, 0x0B24, 0x0B25, 0x0540, 0x0514]

def main():
   parser = argparse.ArgumentParser(description="Si5342 config tool")

   parser.add_argument("-w", "--write", type=str, required=False, help="write configuration")
   parser.add_argument("-v", "--verify", type=str, required=False, help="verify configuration")
   parser.add_argument("-r", "--reset", action="store_true", required=False, help="reset PLL")
   args = parser.parse_args()

   pll = Si5345(SI5342_I2C_BUS, SI5342_I2C_ADDR)

   if args.reset:
      pll.reset()
      print("I: PLL RESET done")
      sys.exit(0)

   if args.write is None and args.verify is None:
      parser.print_help()
      sys.exit(0)
   elif args.write:
      filename = args.write
   elif args.verify:
      filename = args.verify

   try:
      f = open(filename, "r", encoding="utf-8")
   except FileNotFoundError:
      print(f"E: file '{filename}' not found", file=sys.stderr)
      sys.exit(1)
   except Exception as e:
      print(f"E: {e}", file=sys.stderr)
      sys.exit(1)

   if args.write:
      for line in f:
         if line.startswith('#') or not line.startswith('0x'):
            continue
         addr, value = map(lambda x: int(x, 16), line.split(','))
         pll.write_register(addr, value)
         #print(hex(addr), hex(value))
         #print(line)
         # detect preamble
         if(addr == 0x540 and value == 0x1):
            time.sleep(0.5)
      print("I: Si5345 configuration WRITE: done")

   elif args.verify:
      errors = 0
      for line in f:
         if line.startswith('#') or not line.startswith('0x'):
            continue
         addr, value = map(lambda x: int(x, 16), line.split(','))
         if addr in reserved_regs:
            #print(f"0x{addr:04X} - skipped (reserved)")
            continue
         read_value = pll.read_register(addr)
         if read_value != value:
            print(f"address 0x{addr:04X} value mismatch - expected 0x{value:04X}, read 0x{read_value:04X}")
            errors = errors + 1
      if errors > 0:
         print(f"I: verification failed - {errors} errors")
      else:
         print("I: verification OK - 0 errors")
      print("I: Si5345 configuration VERIFY: done")

   f.close()

if __name__ == "__main__":
    main()
