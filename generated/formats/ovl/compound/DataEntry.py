class DataEntry:

	"""
	32 bytes
	"""

	def __init__(self, arg=None, template=None):
		self.name = ''
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0

		# DJB hash; sometimes matches an archive header's first File Hash
		self.file_hash = 0

		# DJB hash for extension; always (?) matches an archive header's hash
		self.ext_hash = 0
		self.set_index = 0

		# number of buffers that should be read from list for this entry
		self.buffer_count = 0
		self.zero_10 = 0

		# size of first buffer, in the case of the ms2 the size 1 is the sizw of the first two buffers together
		self.size_1 = 0
		self.zero_18 = 0

		# size of last buffer
		self.size_2 = 0
		self.zero_20 = 0

	def read(self, stream):

		self.io_start = stream.tell()
		self.file_hash = stream.read_uint()
		if (((stream.user_version == 24724) or (stream.user_version == 25108)) and ((stream.version == 19) and (stream.version_flag == 1))) or ((((stream.user_version == 8340) or (stream.user_version == 8724)) and (stream.version == 19)) or (((stream.user_version == 24724) or (stream.user_version == 25108)) and ((stream.version == 19) and (stream.version_flag == 8)))):
			self.ext_hash = stream.read_uint()
		self.set_index = stream.read_ushort()
		self.buffer_count = stream.read_ushort()
		if (((stream.user_version == 24724) or (stream.user_version == 25108)) and ((stream.version == 19) and (stream.version_flag == 1))) or ((((stream.user_version == 8340) or (stream.user_version == 8724)) and (stream.version == 19)) or (((stream.user_version == 24724) or (stream.user_version == 25108)) and ((stream.version == 19) and (stream.version_flag == 8)))):
			self.zero_10 = stream.read_uint()
		self.size_1 = stream.read_uint()
		self.zero_18 = stream.read_uint()
		self.size_2 = stream.read_uint()
		self.zero_20 = stream.read_uint()

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):

		self.io_start = stream.tell()
		stream.write_uint(self.file_hash)
		if (((stream.user_version == 24724) or (stream.user_version == 25108)) and ((stream.version == 19) and (stream.version_flag == 1))) or ((((stream.user_version == 8340) or (stream.user_version == 8724)) and (stream.version == 19)) or (((stream.user_version == 24724) or (stream.user_version == 25108)) and ((stream.version == 19) and (stream.version_flag == 8)))):
			stream.write_uint(self.ext_hash)
		stream.write_ushort(self.set_index)
		stream.write_ushort(self.buffer_count)
		if (((stream.user_version == 24724) or (stream.user_version == 25108)) and ((stream.version == 19) and (stream.version_flag == 1))) or ((((stream.user_version == 8340) or (stream.user_version == 8724)) and (stream.version == 19)) or (((stream.user_version == 24724) or (stream.user_version == 25108)) and ((stream.version == 19) and (stream.version_flag == 8)))):
			stream.write_uint(self.zero_10)
		stream.write_uint(self.size_1)
		stream.write_uint(self.zero_18)
		stream.write_uint(self.size_2)
		stream.write_uint(self.zero_20)

		self.io_size = stream.tell() - self.io_start

	def get_info_str(self):
		return f'DataEntry [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self):
		s = ''
		s += f'\n	* file_hash = {self.file_hash.__repr__()}'
		s += f'\n	* ext_hash = {self.ext_hash.__repr__()}'
		s += f'\n	* set_index = {self.set_index.__repr__()}'
		s += f'\n	* buffer_count = {self.buffer_count.__repr__()}'
		s += f'\n	* zero_10 = {self.zero_10.__repr__()}'
		s += f'\n	* size_1 = {self.size_1.__repr__()}'
		s += f'\n	* zero_18 = {self.zero_18.__repr__()}'
		s += f'\n	* size_2 = {self.size_2.__repr__()}'
		s += f'\n	* zero_20 = {self.zero_20.__repr__()}'
		return s

	def __repr__(self):
		s = self.get_info_str()
		s += self.get_fields_str()
		s += '\n'
		return s

	def update_data(self, datas):
		"""Load datas into this DataEntry's buffers, and update its size values according to an assumed pattern
		data : list of bytes object, each representing the data of one buffer for this data entry"""
		for buffer, data in zip(self.buffers, datas):
			buffer.update_data(data)
		# update data 0, 1 size
		total = sum(len(d) for d in datas)
		if len(datas) == 1:
			self.size_1 = len(datas[0])
			self.size_2 = 0
		elif len(datas) == 2:
			self.size_1 = 0
			self.size_2 = sum(len(d) for d in datas)
		elif len(datas) > 2:
			self.size_1 = sum(len(d) for d in datas[:-1])
			self.size_2 = len(datas[-1])


	# print(total)
	# print(self.size_1)
	# print(self.size_2)

	def update_buffers(self, ):
		# sort the buffer entries of each data entry by their index
		self.buffers.sort(key=lambda buffer: buffer.index)


	# trim to valid buffers (ignore ones that run out of count, usually zero-sized ones)
	# self.buffers = self.buffers[:self.buffer_count]
	# self.buffers = list(b for b in self.buffers if b.size)

	@property
	def buffer_datas(self):
		"""Get data for each non-empty buffer (should have been sorted before)"""
		return list(buffer.data for buffer in self.buffers if buffer.size)
