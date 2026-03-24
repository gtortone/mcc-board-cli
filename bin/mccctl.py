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

   mcc = MCCBoard()

   # sw
   sw_parser = cmd2.Cmd2ArgumentParser()
   sw_subparser = sw_parser.add_subparsers(title='subcommands', help='subcommand help')

   sw_port_parser = sw_subparser.add_parser('port')
   sw_port_parser.add_argument('num', type=int, help='port number')
   sw_port_parser.add_argument('command', choices=['on','off',"keep_power", "auto_power"], help='command')

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
   fpga_status_parser = fpga_subparser.add_parser('status', help='print FPGA status')

   # timing
   timing_parser = cmd2.Cmd2ArgumentParser()
   timing_subparser = timing_parser.add_subparsers(title='subcommands', help='subcommand help')

   timing_status_parser = timing_subparser.add_parser('status', help='print timing system status')

   # board
   board_parser = cmd2.Cmd2ArgumentParser()
   board_subparser = board_parser.add_subparsers(title='subcommands', help='subcommand help')

   board_status_parser = board_subparser.add_parser('status', help='print board status')

   # host
   host_parser = cmd2.Cmd2ArgumentParser()
   host_subparser = host_parser.add_subparsers(title='subcommands', help='subcommand help')

   host_status_parser = host_subparser.add_parser('status', help='print board status')

   def swport(self, args):
      if args.command == 'on':
         print(f"turn on port {args.num}")
         self.mcc.sw.port_on(args.num) 
      elif args.command == 'off':
         print(f"turn off port {args.num}")
         self.mcc.sw.port_off(args.num) 
      elif args.command == 'keep_power':
         self.mcc.sw.port_set_keep_power(args.num, True)
      elif args.command == 'auto_power':
         self.mcc.sw.port_set_keep_power(args.num, False)

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
               round(self.mcc.sw.port_power(port), 2),
               self.mcc.sw.port_get_keep_power(port)
            ])
         i += 1
      
      print()
      print(tabulate(data_ctrl, headers=["controller", "voltage [V]", "temperature [C]"], tablefmt="simple"))
      print()
      print(tabulate(data_port, headers=["port", "switch", "class", "detection", "voltage [V]",
         "current [mA]", "power [W]", "keep power"], tablefmt="simple"))
      print()

   def sfpstatus(self, args):
      data = []
      for i, sfp in enumerate(self.mcc.sfp):
         if not sfp.is_available() or sfp.connector_type() != sfp.LC_CONNECTOR_TYPE:
            data.append([f"SFP #{i}", sfp.power_status_str()])
         else:
            data.append([f"SFP #{i}",
               sfp.power_status_str(),
               sfp.voltage(),
               sfp.temperature(),
               sfp.tx_bias(),
               sfp.tx_power(),
               sfp.rx_power()
            ])
      print()
      print(tabulate(data, headers=["module", "switch", "voltage [V]", "temperature [C]", 
         "tx bias [mA]", "tx power [uW]", "rx power [uW]"], tablefmt="simple"))
      print()

   def sfpinfo(self, args):
      data = []
      for i, sfp in enumerate(self.mcc.sfp):
         if not sfp.is_available():
            data.append([f"SFP #{i}", sfp.power_status_str()])
         else:
            data.append([f"SFP #{i}",
               sfp.power_status_str(),
               sfp.vendor(),
               sfp.model(),
               sfp.serial(),
               sfp.datecode()
            ])
      print()
      print(tabulate(data, headers=["module", "switch", "vendor", "model", 
         "serial", "datecode"], tablefmt="simple"))
      print()
      None

   def sfpport(self, args):
      if self.mcc.version == 1:
         print("'sfp port' command not available for MCCv1")
         return
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
      print(f"release/tag: {ver['release']}, build: {ver['build_date']}/{ver['build_time']}, commit: {ver['commit_date']}/{ver['commit_hash']}")

   def fpgastatus(self, args):
      table = []
      data = self.mcc.fpga.read_ams()
      for d in data:
         if d['type'] == 'voltage':
            table.append([d['channel'], d['value'], ""])
         elif d['type'] == 'temp':
            table.append([d['channel'], "", d['value']])
      print()
      table_sorted = sorted(table, key=lambda x: x[0])
      print(tabulate(table_sorted, headers=["channel", "voltage [V]", "temperature [C]"], 
         tablefmt="simple", colalign=("left", "decimal", "decimal")))
      print() 
         
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
      for i, sfpmon in enumerate(self.mcc.sfpmon):
         data.append([f"SFP #{i}",
            round(sfpmon.voltage(), 2), 
            round(sfpmon.current() * 1000, 2),
            round(sfpmon.power(), 2),
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
         colalign=("left", "decimal", "decimal", "decimal")))
      print()

   def timingstatus(self, args):
      tstatus = self.mcc.fpga.get_timing_status() 
      
      data = []
      for k,v in tstatus.items():
         data.append([k, v])

      print()
      print(tabulate(data, headers=["parameter", "status"], tablefmt="simple"))
      print()

   def hoststatus(self, args):
      data = []

      cpu = self.mcc.host.get_cpu_status()
      for i, value in enumerate(cpu):
         data.append([f"CPU #{i}", value])

      print()
      print(tabulate(data, headers=["CPU", "usage [%]"], tablefmt="simple", colalign=("left", "decimal")))
      print() 

      data = []
      mem = self.mcc.host.get_memory_status()
      data.append(["RAM total", round(mem.total / 1e6, 0)]) 
      data.append(["RAM available", round(mem.available / 1e6, 0), round(mem.available/mem.total*100, 2)]) 
      data.append(["RAM used", round(mem.used/ 1e6, 0), round(mem.used/mem.total*100, 2)]) 
      
      print()
      print(tabulate(data, headers=["memory", "megabytes [MB]", "percent [%]"], tablefmt="simple"))
      print()
               
      data = []
      net = self.mcc.host.get_network_status()
      for intf, d in net.items():
         data.append([f"{intf}", d["rx_speed"], d["tx_speed"]]) 

      print()
      print(tabulate(data, headers=["network", "rx (Mbit/s)", "tx (Mbit/s)"], tablefmt="simple"))
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
   fpga_status_parser.set_defaults(func=fpgastatus)
   host_status_parser.set_defaults(func=hoststatus)
   board_status_parser.set_defaults(func=boardstatus)
   timing_status_parser.set_defaults(func=timingstatus)

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
      if self.mcc.version == 1:
         print("'board' command not available for MCCv1")
         return 
      func = getattr(args, 'func', None)
      if func is not None:
         func(self, args)
      else:
         self.do_help('board')

   @cmd2.with_argparser(timing_parser)
   def do_timing(self, args):
      if self.mcc.version == 1:
         print("'timing' command not available for MCCv1")
         return
      func = getattr(args, 'func', None)
      if func is not None:
         func(self, args)
      else:
         self.do_help('timing')

   @cmd2.with_argparser(host_parser)
   def do_host(self, args):
      func = getattr(args, 'func', None)
      if func is not None:
         func(self, args)
      else:
         self.do_help('host')

if __name__ == '__main__':
   c = App()
   sys.exit(c.cmdloop())
