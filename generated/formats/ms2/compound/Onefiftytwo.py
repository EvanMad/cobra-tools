from generated.formats.ms2.compound.CoreModelInfo import CoreModelInfo
import typing


class Onefiftytwo:

	"""
	# equivalent to 38 uints, 152 bytes
	"""
	model_info: CoreModelInfo
	some: typing.List[int]

	def __init__(self, arg=None, template=None):
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.model_info = CoreModelInfo()
		self.some = []

	def read(self, stream):

		io_start = stream.tell()
		self.model_info = stream.read_type(CoreModelInfo)
		self.some = [stream.read_uint64() for _ in range(7)]

		self.io_size = stream.tell() - io_start

	def write(self, stream):

		io_start = stream.tell()
		stream.write_type(self.model_info)
		for item in self.some: stream.write_uint64(item)

		self.io_size = stream.tell() - io_start

	def __repr__(self):
		s = 'Onefiftytwo [Size: '+str(self.io_size)+']'
		s += '\n	* model_info = ' + self.model_info.__repr__()
		s += '\n	* some = ' + self.some.__repr__()
		s += '\n'
		return s