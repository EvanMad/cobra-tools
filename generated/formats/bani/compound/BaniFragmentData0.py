class BaniFragmentData0:

	"""
	This varies per bani animation file and describes the bani's frames and duration
	"""

	def __init__(self, arg=None, template=None):
		self.name = ''
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0
		self.unknown_0 = 0
		self.unknown_1 = 0

		# The frame in the banis where this bani starts reading
		self.read_start_frame = 0

		# Number of frames in this bani file
		self.num_frames = 0

		# length of the animation, can easily get keyframe spacing now
		self.animation_length = 0

		# if 1381323599 then looped
		self.loop_flag = 0

	def read(self, stream):

		self.io_start = stream.tell()
		self.unknown_0 = stream.read_uint()
		self.unknown_1 = stream.read_uint()
		self.read_start_frame = stream.read_uint()
		self.num_frames = stream.read_uint()
		self.animation_length = stream.read_float()
		self.loop_flag = stream.read_uint()

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):

		self.io_start = stream.tell()
		stream.write_uint(self.unknown_0)
		stream.write_uint(self.unknown_1)
		stream.write_uint(self.read_start_frame)
		stream.write_uint(self.num_frames)
		stream.write_float(self.animation_length)
		stream.write_uint(self.loop_flag)

		self.io_size = stream.tell() - self.io_start

	def get_info_str(self):
		return f'BaniFragmentData0 [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self):
		s = ''
		s += f'\n	* unknown_0 = {self.unknown_0.__repr__()}'
		s += f'\n	* unknown_1 = {self.unknown_1.__repr__()}'
		s += f'\n	* read_start_frame = {self.read_start_frame.__repr__()}'
		s += f'\n	* num_frames = {self.num_frames.__repr__()}'
		s += f'\n	* animation_length = {self.animation_length.__repr__()}'
		s += f'\n	* loop_flag = {self.loop_flag.__repr__()}'
		return s

	def __repr__(self):
		s = self.get_info_str()
		s += self.get_fields_str()
		s += '\n'
		return s
