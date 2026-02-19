
import mmap

class FPGADevice:

   def __init__(self, uiodev):
      try:
         self.fid = open(uiodev, 'r+b', 0)
      except FileNotFoundError:
         self.perror("UIO device not found")
         sys.exit(-1)

      self.regs = mmap.mmap(self.fid.fileno(), 0x10000)

   def read_register(self, add) -> int:
      return int.from_bytes(self.regs[add*4:(add*4)+4], byteorder='little')

   def write_register(self, add, value) -> None:
      self.regs[add*4:(add*4)+4] = int.to_bytes(value, 4, byteorder='little') 

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
         value[6:8],
      ))

      return { 
         "build_date": build_date, 
         "build_time": build_time,
         "commit_date": commit_date,
         "commit_hash": commit_hash
      }
