
import os
import re
import mmap

class FPGADevice:

   ams_channel_label = [
      "ctrl_vcc_pspll0",
      "ctrl_vcc_psbatt",
      "ctrl_vccint",
      "ctrl_vccbram",
      "ctrl_vccaux",
      "ctrl_vcc_psddrpll",
      "ctrl_vccpsintfpddr",
      "ps_temp",
      "ps_remote_temp",
      "ps_vccpsintlp",
      "ps_vccpsintfp",
      "ps_vccpsaux",
      "ps_vccpsddr",
      "ps_vccpsio3",
      "ps_vccpsio0",
      "ps_vccpsio1",
      "ps_vccpsio2",
      "ps_psmgtravcc",
      "ps_psmgtravtt",
      "ps_vccams",
      "pl_temp",
      "pl_vccint",
      "pl_vccaux",
      "pl_vccvrefp",
      "pl_vccvrefn",
      "pl_vccbram",
      "pl_vccplintlp",
      "pl_vccplintfp",
      "pl_vccplaux",
      "pl_vccams"
   ]

   def __init__(self, uiodev):
      try:
         self.fid = open(uiodev, 'r+b', 0)
      except FileNotFoundError:
         self.perror("UIO device not found")
         sys.exit(-1)

      self.regs = mmap.mmap(self.fid.fileno(), 0x10000)

      # init AMS
      self.ams = []
      self.ams_basedir = '/sys/bus/iio/devices/iio:device0/'
      files = os.listdir(self.ams_basedir) 
      filtered_files = [file for file in files if file.startswith('in_') and file.endswith('_raw')]
      for file in filtered_files:
         extracted_string = file[len('in_'):-len('_raw')]
         match = re.match(r"([a-zA-Z]+)(\d+)$", extracted_string)
         if match:
            type = match.group(1)
            ch = int(match.group(2))
            d = {
               'label': self.ams_channel_label[ch],
               'type': type,
               'channel': ch
            }

            # read offset and scale
            prefix = "in_" + type + str(ch)
            try:
               with open(self.ams_basedir + prefix + "_offset", 'r') as file:
                  d['offset'] = int(file.read().strip())
            except:
               ...

            prefix = "in_" + type + str(ch)
            try:
               with open(self.ams_basedir + prefix + "_scale", 'r') as file:
                  d['scale'] = float(file.read().strip())
            except:
               ...

            self.ams.append(d)
      
   def read_register(self, add) -> int:
      return int.from_bytes(self.regs[add*4:(add*4)+4], byteorder='little')

   def write_register(self, add, value) -> None:
      self.regs[add*4:(add*4)+4] = int.to_bytes(value, 4, byteorder='little') 

   def read_ams(self):
      out = []
      for m in self.ams:
         filename = "in_" + m['type'] + str(m['channel']) + "_raw"
         with open(self.ams_basedir + filename, 'r') as file:
            raw = int(file.read().strip())
            offset = m.get('offset', 0)
            scale = m.get('scale', 1)
            value = round(((raw + offset) * scale) / 1000, 2)
            d = { "channel": m['label'], "value": value, "type": m['type'] }
            out.append(d)
      return out 

   def get_timing_status(self):
      value = self.read_register(10);
      data = {}
      data['MCC-MCC timing link locked'] = bool(value & (1 << 8))
      data['Si5345 PLL locked'] = bool(value & (1 << 4))
      data['TDM-MCC timing link locked'] = bool(value & 1)
      return data

   def bitstream_version(self):
      commit_hash = hex(self.read_register(0))[2:]

      value = hex(self.read_register(1))[2:].zfill(8)
      commit_date = ''.join((
         value[0:2],
         '.',
         value[2:4],
         '.',
         value[4:8]
      ))
       
      value = hex(self.read_register(3))[2:].zfill(8)      
      build_date = ''.join((
         value[6:8],
         '.',
         value[4:6],
         '.',
         value[0:4]
      ))

      value = hex(self.read_register(2))[2:].zfill(8)
      build_time = ''.join((
         value[0:2],
         ':',
         value[2:4],
         ':',
         value[4:6],
         '.',
         value[6:8]
      ))

      value = hex(self.read_register(4))[2:].zfill(8)
      release = ''.join((
         str(int(value[0:2])),
         '.',
         str(int(value[2:4])),
         '.',
         str(int(value[4:8]))
      ))
      

      return { 
         "build_date": build_date, 
         "build_time": build_time,
         "commit_date": commit_date,
         "commit_hash": commit_hash,
         "release": release
      }

