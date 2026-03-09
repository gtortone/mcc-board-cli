
import psutil

from lib.NetworkMonitor import NetworkMonitor

class Host:

   def __init__(self):
      self.netmon = NetworkMonitor()

   def get_cpu_status(self):
      return(psutil.cpu_percent(interval=1, percpu=True))

   def get_memory_status(self):
      return(psutil.virtual_memory())

   def get_network_status(self):
      return self.netmon.get_bandwith()

