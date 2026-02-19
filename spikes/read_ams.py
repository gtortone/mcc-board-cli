#!/usr/bin/env python3

import os
import re

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

ams = []

basedir = '/sys/bus/iio/devices/iio:device0/'

files = os.listdir(basedir)

filtered_files = [file for file in files if file.startswith('in_') and file.endswith('_raw')]

for file in filtered_files:
   extracted_string = file[len('in_'):-len('_raw')]
    
   match = re.match(r"([a-zA-Z]+)(\d+)$", extracted_string)
    
   if match:
      type = match.group(1)
      ch = int(match.group(2))
      d = { 
         'label': ams_channel_label[ch], 
         'type': type,
         'channel': ch
      } 

      # read offset and scale
      prefix = "in_" + type + str(ch)
      try:
         with open(basedir + prefix + "_offset", 'r') as file:
            d['offset'] = int(file.read().strip())
      except:
         ...

      prefix = "in_" + type + str(ch)
      try:
         with open(basedir + prefix + "_scale", 'r') as file:
            d['scale'] = float(file.read().strip())
      except:
         ...

      ams.append(d)

# sample AMS channels
out = [] 
for m in ams:
   filename = "in_" + m['type'] + str(m['channel']) + "_raw"
   with open(basedir + filename, 'r') as file:
      raw = int(file.read().strip())
      offset = m.get('offset', 0)
      scale = m.get('scale', 1)
      value = round(((raw + offset) * scale) / 1000, 2)
      d = { "channel": m['label'], "value": value, "type": m['type'] }
      out.append(d) 

print(out)
