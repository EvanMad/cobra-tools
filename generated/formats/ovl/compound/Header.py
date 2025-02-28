import typing
from generated.array import Array
from generated.formats.ovl.bitfield.VersionInfo import VersionInfo
from generated.formats.ovl.compound.ArchiveEntry import ArchiveEntry
from generated.formats.ovl.compound.AuxEntry import AuxEntry
from generated.formats.ovl.compound.DirEntry import DirEntry
from generated.formats.ovl.compound.FileEntry import FileEntry
from generated.formats.ovl.compound.FixedString import FixedString
from generated.formats.ovl.compound.MimeEntry import MimeEntry
from generated.formats.ovl.compound.TextureEntry import TextureEntry
from generated.formats.ovl.compound.UnknownEntry import UnknownEntry
from generated.formats.ovl.compound.ZStringBuffer import ZStringBuffer
from generated.formats.ovl.compound.ZlibInfo import ZlibInfo


class Header:

	"""
	Found at the beginning of every OVL file
	"""

	def __init__(self, arg=None, template=None):
		self.name = ''
		self.arg = arg
		self.template = template
		self.io_size = 0
		self.io_start = 0

		# 'FRES'
		self.fres = FixedString()

		# if 0x08 then 64bit, differentiates between ED and JWE, 0x08 for ED and PC
		self.version_flag = 0

		# 0x12 = PC, 0x13 = JWE, PZ
		self.version = 0

		# endianness?, usually zero
		self.bitswap = 0

		# always = 1
		self.seventh_byte = 1

		# determines compression format (none, zlib or oodle) and apparently type of data (additional fields)
		self.user_version = VersionInfo()

		# always = 0
		self.zero = 0

		# length of the Names block below, including 00 bytes
		self.len_names = 0

		# always = 0
		self.zero_2 = 0

		# count of external aux files, ie audio banks
		self.num_aux_entries = 0

		# count of directories
		self.num_dirs = 0

		# count of file mime types, aka. extensions with metadata
		self.num_mimes = 0

		# count of files
		self.num_files = 0

		# repeat count of files ??
		self.num_files_2 = 0

		# count of parts
		self.num_textures = 0

		# number of archives
		self.num_archives = 0

		# number of header types across all archives
		self.num_header_types = 0

		# number of headers of all types across all archives
		self.num_headers = 0

		# number of DataEntries across all archives
		self.num_datas = 0

		# number of BufferEntries across all archives
		self.num_buffers = 0

		# number of files in external OVS archive
		self.num_files_ovs = 0

		# used in ZTUAC elephants
		self.ztuac_unknowns = Array()

		# length of archive names
		self.len_archive_names = 0

		# another Num Files
		self.num_files_3 = 0

		# length of the type names portion insideNames block (usually at the start), not counting 00 bytes
		self.len_type_names = 0

		# 52 bytes zeros
		self.zeros_2 = Array()

		# Name buffer for assets and file mime types.
		self.names = ZStringBuffer()

		# Array of MimeEntry objects that represent a mime type (file extension) each.
		self.mimes = Array()

		# Array of FileEntry objects.
		self.files = Array()

		# Name buffer for archives, usually will be STATIC followed by any OVS names
		self.archive_names = ZStringBuffer()

		# Array of ArchiveEntry objects.
		self.archives = Array()

		# Array of DirEntry objects.
		self.dirs = Array()

		# Array of TextureEntry objects.
		self.textures = Array()

		# Array of AuxEntry objects.
		self.aux_entries = Array()

		# Array of UnknownEntry objects.
		self.unknowns = Array()

		# repeats by archive count
		self.zlibs = Array()

	def read(self, stream):

		self.io_start = stream.tell()
		self.fres = stream.read_type(FixedString, (4,))
		self.version_flag = stream.read_byte()
		stream.version_flag = self.version_flag
		self.version = stream.read_byte()
		stream.version = self.version
		self.bitswap = stream.read_byte()
		self.seventh_byte = stream.read_byte()
		self.user_version = stream.read_type(VersionInfo)
		stream.user_version = self.user_version
		self.zero = stream.read_uint()
		self.len_names = stream.read_uint()
		self.zero_2 = stream.read_uint()
		self.num_aux_entries = stream.read_uint()
		self.num_dirs = stream.read_ushort()
		self.num_mimes = stream.read_ushort()
		self.num_files = stream.read_uint()
		self.num_files_2 = stream.read_uint()
		self.num_textures = stream.read_uint()
		self.num_archives = stream.read_uint()
		self.num_header_types = stream.read_uint()
		self.num_headers = stream.read_uint()
		self.num_datas = stream.read_uint()
		self.num_buffers = stream.read_uint()
		self.num_files_ovs = stream.read_uint()
		self.ztuac_unknowns = stream.read_uints((3))
		self.len_archive_names = stream.read_uint()
		self.num_files_3 = stream.read_uint()
		self.len_type_names = stream.read_uint()
		self.zeros_2 = stream.read_bytes((52))
		self.names = stream.read_type(ZStringBuffer, (self.len_names,))
		self.mimes.read(stream, MimeEntry, self.num_mimes, None)
		self.files.read(stream, FileEntry, self.num_files, None)
		self.archive_names = stream.read_type(ZStringBuffer, (self.len_archive_names,))
		self.archives.read(stream, ArchiveEntry, self.num_archives, None)
		self.dirs.read(stream, DirEntry, self.num_dirs, None)
		self.textures.read(stream, TextureEntry, self.num_textures, None)
		self.aux_entries.read(stream, AuxEntry, self.num_aux_entries, None)
		self.unknowns.read(stream, UnknownEntry, self.num_files_ovs, None)
		self.zlibs.read(stream, ZlibInfo, self.num_archives, None)

		self.io_size = stream.tell() - self.io_start

	def write(self, stream):

		self.io_start = stream.tell()
		stream.write_type(self.fres)
		stream.write_byte(self.version_flag)
		stream.version_flag = self.version_flag
		stream.write_byte(self.version)
		stream.version = self.version
		stream.write_byte(self.bitswap)
		stream.write_byte(self.seventh_byte)
		stream.write_type(self.user_version)
		stream.user_version = self.user_version
		stream.write_uint(self.zero)
		stream.write_uint(self.len_names)
		stream.write_uint(self.zero_2)
		stream.write_uint(self.num_aux_entries)
		stream.write_ushort(self.num_dirs)
		stream.write_ushort(self.num_mimes)
		stream.write_uint(self.num_files)
		stream.write_uint(self.num_files_2)
		stream.write_uint(self.num_textures)
		stream.write_uint(self.num_archives)
		stream.write_uint(self.num_header_types)
		stream.write_uint(self.num_headers)
		stream.write_uint(self.num_datas)
		stream.write_uint(self.num_buffers)
		stream.write_uint(self.num_files_ovs)
		stream.write_uints(self.ztuac_unknowns)
		stream.write_uint(self.len_archive_names)
		stream.write_uint(self.num_files_3)
		stream.write_uint(self.len_type_names)
		stream.write_bytes(self.zeros_2)
		stream.write_type(self.names)
		self.mimes.write(stream, MimeEntry, self.num_mimes, None)
		self.files.write(stream, FileEntry, self.num_files, None)
		stream.write_type(self.archive_names)
		self.archives.write(stream, ArchiveEntry, self.num_archives, None)
		self.dirs.write(stream, DirEntry, self.num_dirs, None)
		self.textures.write(stream, TextureEntry, self.num_textures, None)
		self.aux_entries.write(stream, AuxEntry, self.num_aux_entries, None)
		self.unknowns.write(stream, UnknownEntry, self.num_files_ovs, None)
		self.zlibs.write(stream, ZlibInfo, self.num_archives, None)

		self.io_size = stream.tell() - self.io_start

	def get_info_str(self):
		return f'Header [Size: {self.io_size}, Address: {self.io_start}] {self.name}'

	def get_fields_str(self):
		s = ''
		s += f'\n	* fres = {self.fres.__repr__()}'
		s += f'\n	* version_flag = {self.version_flag.__repr__()}'
		s += f'\n	* version = {self.version.__repr__()}'
		s += f'\n	* bitswap = {self.bitswap.__repr__()}'
		s += f'\n	* seventh_byte = {self.seventh_byte.__repr__()}'
		s += f'\n	* user_version = {self.user_version.__repr__()}'
		s += f'\n	* zero = {self.zero.__repr__()}'
		s += f'\n	* len_names = {self.len_names.__repr__()}'
		s += f'\n	* zero_2 = {self.zero_2.__repr__()}'
		s += f'\n	* num_aux_entries = {self.num_aux_entries.__repr__()}'
		s += f'\n	* num_dirs = {self.num_dirs.__repr__()}'
		s += f'\n	* num_mimes = {self.num_mimes.__repr__()}'
		s += f'\n	* num_files = {self.num_files.__repr__()}'
		s += f'\n	* num_files_2 = {self.num_files_2.__repr__()}'
		s += f'\n	* num_textures = {self.num_textures.__repr__()}'
		s += f'\n	* num_archives = {self.num_archives.__repr__()}'
		s += f'\n	* num_header_types = {self.num_header_types.__repr__()}'
		s += f'\n	* num_headers = {self.num_headers.__repr__()}'
		s += f'\n	* num_datas = {self.num_datas.__repr__()}'
		s += f'\n	* num_buffers = {self.num_buffers.__repr__()}'
		s += f'\n	* num_files_ovs = {self.num_files_ovs.__repr__()}'
		s += f'\n	* ztuac_unknowns = {self.ztuac_unknowns.__repr__()}'
		s += f'\n	* len_archive_names = {self.len_archive_names.__repr__()}'
		s += f'\n	* num_files_3 = {self.num_files_3.__repr__()}'
		s += f'\n	* len_type_names = {self.len_type_names.__repr__()}'
		s += f'\n	* zeros_2 = {self.zeros_2.__repr__()}'
		s += f'\n	* names = {self.names.__repr__()}'
		s += f'\n	* mimes = {self.mimes.__repr__()}'
		s += f'\n	* files = {self.files.__repr__()}'
		s += f'\n	* archive_names = {self.archive_names.__repr__()}'
		s += f'\n	* archives = {self.archives.__repr__()}'
		s += f'\n	* dirs = {self.dirs.__repr__()}'
		s += f'\n	* textures = {self.textures.__repr__()}'
		s += f'\n	* aux_entries = {self.aux_entries.__repr__()}'
		s += f'\n	* unknowns = {self.unknowns.__repr__()}'
		s += f'\n	* zlibs = {self.zlibs.__repr__()}'
		return s

	def __repr__(self):
		s = self.get_info_str()
		s += self.get_fields_str()
		s += '\n'
		return s
