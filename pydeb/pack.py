# module imports
from multiprocessing.pool import ThreadPool
from os import listdir
from pathlib import Path
from shutil import copytree, rmtree
from subprocess import getoutput
from tarfile import GNU_FORMAT
import xtarfile as tarfile
from zstandard import ZstdCompressionParameters

# local imports
from .control import Control
from .utils import cmd_in_path


class Pack:
	def __init__(self, path: Path, algorithm: str = 'xz', compression_level: int = 9):
		# check if path is Path
		if type(path) is not Path: path = Path(path)
		# path to pack
		self.path = path
		# algo
		self.algorithm = algorithm
		# level
		self.level = compression_level
		# path of deb
		self.debpath = ''
		self.__pack()

	def __compress_object(self, algo: str, tmp, dir_name):
		archive_name = 'data.tar'
		if dir_name == 'DEBIAN': archive_name = 'control.tar'
		if algo == 'xz':
			# create archive
			with tarfile.open(f'{tmp}/{archive_name}.{algo}', f'w:{algo}', preset=self.level, format=GNU_FORMAT) as tar:
				tar.add(f'{tmp}/{dir_name}', arcname='.')
				tar.close()
		elif algo == 'zst':
			params = ZstdCompressionParameters(format=GNU_FORMAT).from_level(self.level)
			# create archive
			with tarfile.open(f'{tmp}/{archive_name}.{algo}', f'w:{algo}', compression_params=params) as tar:
				tar.add(f'{tmp}/{dir_name}', arcname='.')
				tar.close()
		else:
			# create archive
			with tarfile.open(f'{tmp}/{archive_name}.{algo}', f'w:{algo}', compresslevel=self.level, format=GNU_FORMAT) as tar:
				tar.add(f'{tmp}/{dir_name}', arcname='.')
				tar.close()


	def __pack(self):
		# check if path exists
		if not self.path.exists():
			raise Exception(f'Passed file {self.path} does not exist.')
		# check if path is correct
		if not self.path.is_dir():
			raise Exception(
				f'Passed file {self.path} is not a directory file.')
		# check if DEBIAN exists
		if not Path(f'{self.path}/DEBIAN/control').exists():
			raise Exception(f'DEBIAN/control does not exist.')
		# get ar command
		ar = cmd_in_path('ar')
		# ensure file exists
		if ar == None:
			raise Exception(
				'Command "ar" is not installed. Please install it in order to use this library.')
		# ensure algorithm is valid
		if self.algorithm not in ['xz', 'gzip', 'bzip2', 'zstd']:
			raise Exception(
				f'Invalid algorithm type {self.algorithm}. Valid types are: xz, gzip, bzip2. Default is xz.')
		# ensure compression level is valid
		if self.level < 1 or self.level > 9:
			raise Exception(
				f'Invalid compression level {self.level}. Valid levels are 1-9. Default is 9.')
		# formatted path
		with open(f'{self.path}/DEBIAN/control', 'r') as f:
			control = Control(f.read())
			self.debpath = f'{control.package}_{control.version}_{control.architecture}.deb'
		# tmp dir
		tmp = Path(f'.{self.path.name}.pack.tmp')
		# remove tmp dir if it exists
		if tmp.exists():
			rmtree(tmp)
		# loop through files
		for f in listdir(self.path):
			if f == 'DEBIAN':
				copytree(f'{self.path}/{f}', f'{tmp}/DEBIAN')
			else:
				copytree(f'{self.path}/{f}', f'{tmp}/FILESYSTEM/{f}')

		# format algo var
		if self.algorithm == 'gzip':
			self.algorithm = 'gz'
		if self.algorithm == 'bzip2':
			self.algorithm = 'bz2'
		if self.algorithm == 'zstd':
			self.algorithm = 'zst'

		with ThreadPool() as pool:
			pool.starmap(self.__compress_object, [(self.algorithm, tmp, 'DEBIAN'), (self.algorithm, tmp, 'FILESYSTEM')])

		# create binary
		with open(f'{tmp}/debian-binary', 'w') as f:
			f.write('2.0\n')
			f.close()

		# delete paths
		rmtree(f'{tmp}/DEBIAN')
		rmtree(f'{tmp}/FILESYSTEM')

		# create deb
		getoutput(f'{ar} r {self.debpath} {tmp}/debian-binary {tmp}/control.tar.* {tmp}/data.tar.*')

		# delete tmp
		rmtree(tmp)
