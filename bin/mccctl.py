#!/usr/bin/env python3

import sys
import os
import cmd2
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from tabulate import tabulate
from lib.MCCBoard import MCCBoard

class App(cmd2.Cmd):
   def __init__(self):
      super().__init__(persistent_history_file='~/.mccctl_history', persistent_history_length=100)
      self.prompt = "MCC> "

   if((mcc_ver := os.environ.get('MCC_MAJOR_VER')) is None):
      print("E: MCC_MAJOR_VER env variable missing")
      sys.exit(-1)

   mcc = MCCBoard(mcc_ver)
   
   # sw
   sw_parser = cmd2.Cmd2ArgumentParser()
   sw_subparser = sw_parser.add_subparsers(title='subcommands', help='subcommand help')

   sw_port_parser = sw_subparser.add_parser('port')
   sw_port_parser.add_argument('num', type=int, help='port number')
   sw_port_parser.add_argument('command', choices=['on','off'], help='command')

   sw_status_parser = sw_subparser.add_parser('status', help='print switch status')

   # sfp
   sfp_parser = cmd2.Cmd2ArgumentParser()
   sfp_subparser = sfp_parser.add_subparsers(title='subcommands', help='subcommand help')

   sfp_status_parser = sfp_subparser.add_parser('status', help='print SFP status')
   sfp_info_parser = sfp_subparser.add_parser('info', help='print SFP info')
   sfp_port_parser = sfp_subparser.add_parser('port')
   sfp_port_parser.add_argument('num', type=int, help='port number')
   sfp_port_parser.add_argument('command', choices=['on','off'], help='command')

   # fpga 
   fpga_parser = cmd2.Cmd2ArgumentParser()
   fpga_subparser = fpga_parser.add_subparsers(title='subcommands', help='subcommand help')
   
   fpga_read_parser = fpga_subparser.add_parser('read', help='read FPGA register')
   fpga_read_parser.add_argument('address', help='register address - decimal or hexadecimal (prefix 0x)')

   fpga_write_parser = fpga_subparser.add_parser('write', help='write FPGA register')
   fpga_write_parser.add_argument('address', help='register address - decimal or hexadecimal (prefix 0x)')
   fpga_write_parser.add_argument('value', help='register value - decimal or hexadecimal (prefix 0x)')

   fpga_info_parser = fpga_subparser.add_parser('info', help='print FPGA info')

   # board
   board_parser = cmd2.Cmd2ArgumentParser()
   board_subparser = board_parser.add_subparsers(title='subcommands', help='subcommand help')

   board_status_parser = board_subparser.add_parser('status', help='print board status')

   def swport(self, args):
      if args.command == 'on':
         print(f"turn on port {args.num}")
         self.mcc.sw.port_on(args.num) 
      elif args.command == 'off':
         print(f"turn off port {args.num}")
         self.mcc.sw.port_off(args.num) 

   def swstatus(self, args):
      data_ctrl = [] 
      data_port = []
      i = 0
      for ctrl in self.mcc.sw.poectrl:
         data_ctrl.append([f"POE #{i}", ctrl.voltage_in(), ctrl.temperature()])
         for port in range(4*i,(4*i)+4):
            data_port.append([f"{port}", 'ON' if self.mcc.sw.port_status(port) else 'OFF',
               self.mcc.sw.port_class(port), self.mcc.sw.port_detection(port), 
               round(self.mcc.sw.port_voltage(port), 2),
               round(self.mcc.sw.port_current(port), 2),
               round(self.mcc.sw.port_power(port), 2)
            ])
         i += 1
      
      print()
      print(tabulate(data_ctrl, headers=["controller", "voltage [V]", "temperature [C]"], tablefmt="simple"))
      print()
      print(tabulate(data_port, headers=["port", "switch", "class", "detection", "voltage [V]",
         "current [mA]", "power [W]"], tablefmt="simple"))
      print()

   def sfpstatus(self, args):
      data = []
      for i in range(3):
         if not self.mcc.sfp[i].is_available() or self.mcc.sfp[i].connector_type() != self.mcc.sfp[i].LC_CONNECTOR_TYPE:
            data.append([f"SFP #{i}", self.mcc.sfp[i].power_status_str()])
         else:
            data.append([f"SFP #{i}",
               self.mcc.sfp[i].power_status_str(),
               self.mcc.sfp[i].voltage(),
               self.mcc.sfp[i].temperature(),
               self.mcc.sfp[i].tx_bias(),
               self.mcc.sfp[i].tx_power(),
               self.mcc.sfp[i].rx_power()
            ])
      print()
      print(tabulate(data, headers=["module", "switch", "voltage [V]", "temperature [C]", 
         "tx bias [mA]", "tx power [uW]", "rx power [uW]"], tablefmt="simple"))
      print()

   def sfpinfo(self, args):
      data = []
      for i in range(3):
         if not self.mcc.sfp[i].is_available():
            data.append([f"SFP #{i}", self.mcc.sfp[i].power_status_str()])
         else:
            data.append([f"SFP #{i}",
               self.mcc.sfp[i].power_status_str(),
               self.mcc.sfp[i].vendor(),
               self.mcc.sfp[i].model(),
               self.mcc.sfp[i].serial(),
               self.mcc.sfp[i].datecode()
            ])
      print()
      print(tabulate(data, headers=["module", "switch", "vendor", "model", 
         "serial", "datecode"], tablefmt="simple"))
      print()
      None

   def sfpport(self, args):
      if args.command == 'on':
         print(f"turn on SFP {args.num}")
         self.mcc.sfp[args.num].on()
      elif args.command == 'off':
         print(f"turn off SFP {args.num}")
         self.mcc.sfp[args.num].off() 

   def fpgaread(self, args):
      addr = int(args.address, 0)
      value = self.mcc.fpga.read_register(addr)
      self.poutput(f'0x{value:08x} ({value})')
      
   def fpgawrite(self, args):
      try:
         addr = int(args.address, 0)
         value = int(args.value, 0)
         self.mcc.fpga.write_register(addr, value)
         self.poutput(f'0x{value:08x} ({value})')
      except:
         self.perror(f'Write register error')

   def fpgainfo(self, args):
      ver = self.mcc.fpga.bitstream_version()
      print(f"build: {ver['build_date']}/{ver['build_time']}, commit: {ver['commit_date']}/{ver['commit_hash']}")
   
   def boardstatus(self, args):
      data = []
      data.append(["56V main", 
         round(self.mcc.boardmon[0].voltage(), 2), 
         round(self.mcc.boardmon[0].current() * 1000, 2),
         round(self.mcc.boardmon[0].power(), 2),
         ""
      ])
      data.append(["12V rail", 
         round(self.mcc.boardmon[1].voltage(), 2), 
         round(self.mcc.boardmon[1].current() * 1000, 2), 
         round(self.mcc.boardmon[1].power(), 2),
         "" 
      ])
      for i in range(3):
         data.append([f"SFP #{i}",
            round(self.mcc.sfpmon[i].voltage(), 2), 
            round(self.mcc.sfpmon[i].current() * 1000, 2),
            round(self.mcc.sfpmon[i].power(), 2),
            self.mcc.sfp[i].power_status_str() 
         ])

      print()
      print(tabulate(data, headers=["parameter", "voltage [V]", "current [mA]", "power [W]", "switch"], tablefmt="simple"))
      print()

      data = []
      data.append(["SHT40 sensor", round(self.mcc.sht40.read()[0], 2), round(self.mcc.sht40.read()[1], 2), "-"])
      data.append(["BMP585 sensor", round(self.mcc.bmp585.read()[0], 2), "-", round(self.mcc.bmp585.read()[1]/100, 2)])
     
      print()
      print(tabulate(data, headers=["parameter", "temperature [C]", "humidity [%RH]", "pressure [mbar]"], tablefmt="simple",
         colalign=("left", "right", "right", "right")))
      print()

   sw_port_parser.set_defaults(func=swport)
   sw_status_parser.set_defaults(func=swstatus)
   sfp_status_parser.set_defaults(func=sfpstatus)
   sfp_info_parser.set_defaults(func=sfpinfo)
   sfp_info_parser.set_defaults(func=sfpinfo)
   sfp_port_parser.set_defaults(func=sfpport)
   fpga_read_parser.set_defaults(func=fpgaread)
   fpga_write_parser.set_defaults(func=fpgawrite)
   fpga_info_parser.set_defaults(func=fpgainfo)
   board_status_parser.set_defaults(func=boardstatus)

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

   @cmd2.with_argparser(fpga_parser)
   def do_fpga(self, args):
      func = getattr(args, 'func', None)
      if func is not None:
         func(self, args)
      else:
         self.do_help('fpga')

   @cmd2.with_argparser(board_parser)
   def do_board(self, args):
      func = getattr(args, 'func', None)
      if func is not None:
         func(self, args)
      else:
         self.do_help('board')

if __name__ == '__main__':
   c = App()
   sys.exit(c.cmdloop())
