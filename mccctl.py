#!/usr/bin/env python3

import sys
import os
import cmd2
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from lib.MCCBoard import MCCBoard

class App(cmd2.Cmd):
   def __init__(self):
      super().__init__(persistent_history_file='~/.mccctl_history', persistent_history_length=100)
      self.prompt = "MCC> "

   mcc = MCCBoard()
   
   # sw
   sw_parser = cmd2.Cmd2ArgumentParser()
   sw_subparser = sw_parser.add_subparsers(title='subcommands', help='subcommand help')

   sw_port_parser = sw_subparser.add_parser('port')
   sw_port_parser.add_argument('num', type=int, help='port number')
   sw_port_parser.add_argument('command', choices=['on','off','info'], help='command')

   sw_info_parser = sw_subparser.add_parser('info', help='print switch info')

   # sfp
   sfp_parser = cmd2.Cmd2ArgumentParser()
   sfp_subparser = sfp_parser.add_subparsers(title='subcommands', help='subcommand help')

   sfp_info_parser = sfp_subparser.add_parser('info', help='print SFP info')

   # reg
   reg_parser = cmd2.Cmd2ArgumentParser()
   reg_subparser = reg_parser.add_subparsers(title='subcommands', help='subcommand help')
   
   reg_read_parser = reg_subparser.add_parser('read', help='read FPGA register')
   reg_read_parser.add_argument('address', help='register address - decimal or hexadecimal (prefix 0x)')

   reg_write_parser = reg_subparser.add_parser('write', help='write FPGA register')
   reg_write_parser.add_argument('address', help='register address - decimal or hexadecimal (prefix 0x)')
   reg_write_parser.add_argument('value', help='register value - decimal or hexadecimal (prefix 0x)')

   def swport(self, args):
      if args.command == 'on':
         print(f"turn on port {args.num}")
         self.mcc.sw.port_on(args.num) 
      elif args.command == 'off':
         print(f"turn off port {args.num}")
         self.mcc.sw.port_off(args.num) 
      elif args.command == 'info':
         print()
         s = f"port {args.num}: {'ON' if self.mcc.sw.port_status(args.num) else 'OFF':>3}\n" + \
            f"class: {self.mcc.sw.port_class(args.num)}\n" + \
            f"detection: {self.mcc.sw.port_detection(args.num)}\n" + \
            f"voltage: {self.mcc.sw.port_voltage(args.num)}V\n" + \
            f"current: {self.mcc.sw.port_current(args.num)}mA\n" + \
            f"power: {self.mcc.sw.port_power(args.num)}W"
         print(s)
         print()

   def swinfo(self, args):
      self.mcc.sw.print()

   def sfpinfo(self, args):
      print()
      print("SFP #0")
      if self.mcc.sfp0.is_available():
         self.mcc.sfp0.print()
      else:
         print("not available")
      print()
      print("SFP #1")
      if self.mcc.sfp1.is_available():
         self.mcc.sfp1.print()
      else:
         print("not available")
      print()

   def regread(self, args):
      addr = int(args.address, 0)
      value = self.mcc.fpga.read_register(addr)
      self.poutput(f'0x{value:08x} ({value})')
      
   def regwrite(self, args):
      try:
         addr = int(args.address, 0)
         value = int(args.value, 0)
         self.mcc.fpga.write_register(addr, value)
         self.poutput(f'0x{value:08x} ({value})')
      except:
         self.perror(f'Write register error')

   sw_port_parser.set_defaults(func=swport)
   sw_info_parser.set_defaults(func=swinfo)
   sfp_info_parser.set_defaults(func=sfpinfo)
   reg_read_parser.set_defaults(func=regread)
   reg_write_parser.set_defaults(func=regwrite)

   @cmd2.with_argparser(sw_parser)
   def do_sw(self, args):
      func = getattr(args, 'func', None)
      if func is not None:
         func(self, args)
      else:
         self.do_help('sw')

   @cmd2.with_argparser(sfp_parser)
   def do_sfp(self, args):
      func = getattr(args, 'func', None)
      if func is not None:
         func(self, args)
      else:
         self.do_help('sfp')

   @cmd2.with_argparser(reg_parser)
   def do_reg(self, args):
      func = getattr(args, 'func', None)
      if func is not None:
         func(self, args)
      else:
         self.do_help('reg')

if __name__ == '__main__':
   c = App()
   sys.exit(c.cmdloop())
