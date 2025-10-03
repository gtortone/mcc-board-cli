
import mmap

class FPGARegister:

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
