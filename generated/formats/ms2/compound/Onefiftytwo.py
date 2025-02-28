import typing
from generated.array import Array
from generated.formats.ms2.compound.CoreModelInfo import CoreModelInfo


class Onefiftytwo:

	"""
	# equivalent to 38 uints, 152 bytes
	"""

	def __init__(self, arg=None, template=None):
		self.name = ''
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.model_info = CoreModelInfo()
		self.some = Array()

	def read(self, stream):

		self.io_start = stream.tell()
		self.model_info = stream.read_type(CoreModelInfo)
		self.some = stream.read_uint64s((7))

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):

		self.io_start = stream.tell()
		stream.write_type(self.model_info)
		stream.write_uint64s(self.some)

		self.io_size = stream.tell() - self.io_start

	def get_info_str(self):
		return f'Onefiftytwo [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self):
		s = ''
		s += f'\n	* model_info = {self.model_info.__repr__()}'
		s += f'\n	* some = {self.some.__repr__()}'
		return s

	def __repr__(self):
		s = self.get_info_str()
		s += self.get_fields_str()
		s += '\n'
		return s
