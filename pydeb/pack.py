# module imports
from multiprocessing.pool import ThreadPool
from os import listdir
from pathlib import Path
from shutil import copytree, rmtree
from subprocess import getoutput

# local imports
from .control import Control
from .utils import cmd_in_path


class Pack:
	def __init__(self, path: Path, algorithm: str = 'xz', compression_level: int = 9):
		# check if path is Path
		if type(path) is not Path: path = Path(path)

		# algo
		self.algorithm = algorithm
		# fix algorithms
		if self.algorithm == 'gz':
			self.algorithm = 'gzip'
		elif self.algorithm == 'bz2':
			self.algorithm = 'bzip2'
		elif self.algorithm == 'zst':
			self.algorithm = 'zstd'
		elif self.algorithm == 'lz':
			self.algorithm = 'lzma'

		# file endings
		# handle algorithm
		if self.algorithm == 'zstd': self.ending = 'zst'
		elif self.algorithm == 'gzip': self.ending = 'gz'
		elif self.algorithm == 'bzip2': self.ending = 'bz2'
		else: self.ending = self.algorithm

		# valid algos
		self.valid = ['xz', 'gzip', 'bzip2', 'zstd', 'lzma', 'lz4']
		if self.algorithm not in self.valid:
			raise Exception(
				f'Invalid algorithm type {self.algorithm}. Valid types are: xz, gzip, bzip2, lzma. Default is xz.')

		# get ar command
		self.ar = cmd_in_path('ar')
		# ensure file exists
		if self.ar == None:
			raise Exception(
				'Command "ar" could not be found. Please install it in order to use this library.')

		# get tar command
		self.tar = cmd_in_path('tar')
		# ensure file exists
		if self.tar == None:
			raise Exception(
				'Command "tar" could not be found. Please install it in order to use this library.')

		# get compress command
		self.compress_command = cmd_in_path(self.algorithm)
		# ensure file exists
		if self.compress_command == None:
			raise Exception(
				f'Command "{self.algorithm}" could not be found. Please install it in order to use this library.')
		
		# path to pack
		self.path = path

		# level
		self.level = compression_level

		# path of deb
		self.debpath = ''
		self.__pack()

	def __compress_object(self, algo: str, tmp, dir_name):
		archive_name = 'data.tar'
		if dir_name == 'DEBIAN': archive_name = 'control.tar'
		try:
			getoutput(f'cd {tmp}/{dir_name} && {self.tar} -cf - . | {self.compress_command} -{self.level} -c > ../{archive_name}.{self.ending}')
		except:
			raise Exception(f"Error while compressing directory {dir_name} with {algo} algorithm.")


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
		getoutput(f'{self.ar} r {self.debpath} {tmp}/debian-binary {tmp}/control.tar.{self.ending} {tmp}/data.tar.{self.ending}')

		# delete tmp
		rmtree(tmp)
