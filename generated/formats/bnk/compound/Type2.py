import typing


class Type2:

# Sound SFX/Sound Voice
# 02 -- identifier for Sound SFX section

	# length of this section
	length: int

	# id of this Sound SFX object
	sfx_id: int

	# ?
	const_a: int

	# ?
	const_b: int

	# ?
	didx_id: int

	# ?
	wem_length: int

	# ?
	zerosa: int

	# ?
	zerosb: int

	# ?
	some_id: int

	# ?
	const_c: int

	# ?
	const_d: int

	# ?
	const_e: int

	# ?
	float_a: float

	# four unknown bytes
	zeros_c: typing.List[int]

	# ?
	flag: int

	# ?
	zerosd: int

	# ?
	zerose: int

	def __init__(self, arg=None, template=None):
		self.arg = arg
		self.template = template

	def read(self, stream):
		self.length = stream.read_uint()
		self.sfx_id = stream.read_uint()
		self.const_a = stream.read_uint()
		self.const_b = stream.read_byte()
		self.didx_id = stream.read_uint()
		self.wem_length = stream.read_uint()
		self.zerosa = stream.read_uint()
		self.zerosb = stream.read_uint()
		self.some_id = stream.read_uint()
		self.const_c = stream.read_byte()
		self.const_d = stream.read_byte()
		if self.const_d != 0:
			self.const_e = stream.read_byte()
			self.float_a = stream.read_float()
		self.zeros_c = [stream.read_byte() for _ in range(4)]
		self.flag = stream.read_byte()
		self.zerosd = stream.read_uint()
		self.zerose = stream.read_uint()

	def write(self, stream):
		stream.write_uint(self.length)
		stream.write_uint(self.sfx_id)
		stream.write_uint(self.const_a)
		stream.write_byte(self.const_b)
		stream.write_uint(self.didx_id)
		stream.write_uint(self.wem_length)
		stream.write_uint(self.zerosa)
		stream.write_uint(self.zerosb)
		stream.write_uint(self.some_id)
		stream.write_byte(self.const_c)
		stream.write_byte(self.const_d)
		if self.const_d != 0:
			stream.write_byte(self.const_e)
			stream.write_float(self.float_a)
		for item in self.zeros_c: stream.write_byte(item)
		stream.write_byte(self.flag)
		stream.write_uint(self.zerosd)
		stream.write_uint(self.zerose)

	def __repr__(self):
		s = 'Type2'
		s += '\n	* length = ' + self.length.__repr__()
		s += '\n	* sfx_id = ' + self.sfx_id.__repr__()
		s += '\n	* const_a = ' + self.const_a.__repr__()
		s += '\n	* const_b = ' + self.const_b.__repr__()
		s += '\n	* didx_id = ' + self.didx_id.__repr__()
		s += '\n	* wem_length = ' + self.wem_length.__repr__()
		s += '\n	* zerosa = ' + self.zerosa.__repr__()
		s += '\n	* zerosb = ' + self.zerosb.__repr__()
		s += '\n	* some_id = ' + self.some_id.__repr__()
		s += '\n	* const_c = ' + self.const_c.__repr__()
		s += '\n	* const_d = ' + self.const_d.__repr__()
		s += '\n	* const_e = ' + self.const_e.__repr__()
		s += '\n	* float_a = ' + self.float_a.__repr__()
		s += '\n	* zeros_c = ' + self.zeros_c.__repr__()
		s += '\n	* flag = ' + self.flag.__repr__()
		s += '\n	* zerosd = ' + self.zerosd.__repr__()
		s += '\n	* zerose = ' + self.zerose.__repr__()
		s += '\n'
		return s