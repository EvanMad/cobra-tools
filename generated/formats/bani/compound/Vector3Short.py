class Vector3Short:

	"""
	A signed int16 vector in 3D space (x,y,z).
	"""

	# First coordinate.
	x: int

	# Second coordinate.
	y: int

	# Third coordinate.
	z: int

	def __init__(self, arg=None, template=None):
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.x = 0
		self.y = 0
		self.z = 0

	def read(self, stream):

		io_start = stream.tell()
		self.x = stream.read_short()
		self.y = stream.read_short()
		self.z = stream.read_short()

		self.io_size = stream.tell() - io_start

	def write(self, stream):

		io_start = stream.tell()
		stream.write_short(self.x)
		stream.write_short(self.y)
		stream.write_short(self.z)

		self.io_size = stream.tell() - io_start

	def __repr__(self):
		s = 'Vector3Short [Size: '+str(self.io_size)+']'
		s += '\n	* x = ' + self.x.__repr__()
		s += '\n	* y = ' + self.y.__repr__()
		s += '\n	* z = ' + self.z.__repr__()
		s += '\n'
		return s
