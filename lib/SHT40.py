
import time
from smbus2 import SMBus, i2c_msg

class SHT40:

	CMD_MEASURE_HIGH_PRECISION = 0xFD
	CMD_SOFT_RESET = 0x94

	def __init__(self, i2c_bus, i2c_addr, i2c_select=()):
		self.bus = SMBus(i2c_bus)
		self.i2c_addr = i2c_addr
		self.i2c_select = i2c_select

		self.soft_reset()

	def select(self):
		for func in self.i2c_select:
			func()
	
	def crc8(self, data):
		crc = 0xFF
		for byte in data:
			crc ^= byte
			for _ in range(8):
				if crc & 0x80:
					crc = (crc << 1) ^ 0x31
				else:
					crc <<= 1
				crc &= 0xFF
		return crc
	
	def soft_reset(self):
		self.select()
		self.bus.write_byte(self.i2c_addr, self.CMD_SOFT_RESET)
		time.sleep(0.01)
	
	def read(self):
		self.select()
		self.bus.write_byte(self.i2c_addr, self.CMD_MEASURE_HIGH_PRECISION)
		time.sleep(0.01)
		
		read = i2c_msg.read(self.i2c_addr, 6)
		self.bus.i2c_rdwr(read)
		data = list(read)
		
		if self.crc8(data[0:2]) != data[2]:
			raise ValueError("temperature CRC error")
		
		if self.crc8(data[3:5]) != data[5]:
			raise ValueError("humidity CRC error")
		
		raw_temp = (data[0] << 8) | data[1]
		raw_rh = (data[3] << 8) | data[4]
		
		temperature = -45 + 175 * (raw_temp / 65535.0)
		humidity = -6 + 125 * (raw_rh / 65535.0)
		
		humidity = max(0, min(100, humidity))
		
		return temperature, humidity
