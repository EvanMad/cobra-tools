class FourFragFgm:

	"""
	Sized str entry of 16 bytes
	"""

	def __init__(self, arg=None, template=None):
		self.name = ''
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0

		# Number of Texture Info Entries
		self.texture_count = 0
		self.zero_0 = 0

		# Number of Attribute Info Entries
		self.attribute_count = 0
		self.zero_1 = 0

	def read(self, stream):

		self.io_start = stream.tell()
		self.texture_count = stream.read_uint()
		self.zero_0 = stream.read_uint()
		self.attribute_count = stream.read_uint()
		self.zero_1 = stream.read_uint()

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):

		self.io_start = stream.tell()
		stream.write_uint(self.texture_count)
		stream.write_uint(self.zero_0)
		stream.write_uint(self.attribute_count)
		stream.write_uint(self.zero_1)

		self.io_size = stream.tell() - self.io_start

	def get_info_str(self):
		return f'FourFragFgm [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self):
		s = ''
		s += f'\n	* texture_count = {self.texture_count.__repr__()}'
		s += f'\n	* zero_0 = {self.zero_0.__repr__()}'
		s += f'\n	* attribute_count = {self.attribute_count.__repr__()}'
		s += f'\n	* zero_1 = {self.zero_1.__repr__()}'
		return s

	def __repr__(self):
		s = self.get_info_str()
		s += self.get_fields_str()
		s += '\n'
		return s
