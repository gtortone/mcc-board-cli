#!/usr/bin/env python3

import psutil
import threading
import time
import socket

class NetworkMonitor:
   def __init__(self, interval=2):
      self.interval = interval
      self.bandwith = {}

      self.monitor_thread = threading.Thread(target=self.monitor_traffic_periodically)
      self.monitor_thread.daemon = True
      self.monitor_thread.start()

   def get_data(self):
      data = {}
      net_io = psutil.net_io_counters(pernic=True)
        
      for k,v in net_io.items():
         if k in ['lo', 'bond0', 'sit0']:
            continue

         stats = {
            'rx_bytes': v.bytes_recv,
            'tx_bytes': v.bytes_sent,
         }
         data[k] = stats

      return data

   def get_addr(self):
      data = {}
      addrs = psutil.net_if_addrs()

      for interface, addr_list in addrs.items():
         if interface in ['lo', 'bond0', 'sit0']:
            continue
         data[interface] = {}
         for addr in addr_list:
            if addr.family == psutil.AF_LINK:
               data[interface]['mac'] = addr.address
            elif addr.family == socket.AF_INET:
               data[interface]['ip'] = addr.address

      return data   

   def get_bandwith(self):
      return self.bandwith

   def convert_to_mbps(self, bytes):
      return (bytes * 8) / 1000000  # Mbit/s

   def monitor_traffic_periodically(self):
      prev_data = self.get_data() 

      while True:
         bandwith = {}
         data = self.get_data()
         addr = self.get_addr()
         for intf, values in data.items():
            self.bandwith[intf] = {}
            self.bandwith[intf]['rx_speed'] = round(self.convert_to_mbps(
               (data[intf]['rx_bytes'] - prev_data[intf]['rx_bytes'])) / self.interval, 2)
            self.bandwith[intf]['tx_speed'] = round(self.convert_to_mbps(
               (data[intf]['tx_bytes'] - prev_data[intf]['tx_bytes'])) / self.interval, 2)
            self.bandwith[intf]['mac'] = addr[intf]['mac']
            self.bandwith[intf]['ip'] = addr[intf].get('ip', "")

         prev_data = data
         time.sleep(self.interval)

