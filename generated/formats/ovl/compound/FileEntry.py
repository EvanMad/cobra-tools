class FileEntry:

	"""
	Description of one file in the archive
	"""

	def __init__(self, arg=None, template=None):
		self.name = ''
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0

		# offset in the header's Names block; start offset of zero terminated string
		self.offset = 0

		# this hash is used to retrieve the file name from inside the archive
		self.file_hash = 0

		# could be the number of fragments this file is split into; Or the amount of entries that refer to this file
		self.unkn_0 = 0
		self.unkn_1 = 0

		# index into 'Extensions' array
		self.extension = 0

	def read(self, stream):

		self.io_start = stream.tell()
		self.offset = stream.read_uint()
		self.file_hash = stream.read_uint()
		self.unkn_0 = stream.read_byte()
		self.unkn_1 = stream.read_byte()
		self.extension = stream.read_ushort()

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):

		self.io_start = stream.tell()
		stream.write_uint(self.offset)
		stream.write_uint(self.file_hash)
		stream.write_byte(self.unkn_0)
		stream.write_byte(self.unkn_1)
		stream.write_ushort(self.extension)

		self.io_size = stream.tell() - self.io_start

	def get_info_str(self):
		return f'FileEntry [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self):
		s = ''
		s += f'\n	* offset = {self.offset.__repr__()}'
		s += f'\n	* file_hash = {self.file_hash.__repr__()}'
		s += f'\n	* unkn_0 = {self.unkn_0.__repr__()}'
		s += f'\n	* unkn_1 = {self.unkn_1.__repr__()}'
		s += f'\n	* extension = {self.extension.__repr__()}'
		return s

	def __repr__(self):
		s = self.get_info_str()
		s += self.get_fields_str()
		s += '\n'
		return s
