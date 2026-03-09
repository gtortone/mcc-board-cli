#!/usr/bin/env python3

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import time

from lib.Host import Host

host = Host()

while(True):
   print(host.get_cpu_status())
   print(host.get_memory_status())
   print(host.get_network_status())

   time.sleep(1)
