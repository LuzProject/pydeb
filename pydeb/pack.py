# module imports
import tarfile
from os import listdir, path, system
from pathlib import Path
from shutil import copytree, rmtree

# local imports
from .utils import cmd_in_path


class Pack:
	def __init__(self, path: str, algorithm: str = 'xz', compression_level: int = 9):
		# path to pack
		self.path = path
		# algo
		self.algorithm = algorithm
		# level
		self.level = compression_level
		# path of deb
		self.debpath = ''
		self.__pack()


	def __pack(self):
		# check if path exists
		if not path.exists(self.path):
			raise Exception(f'Passed file {self.path} does not exist.')
		# check if path is correct
		if not path.isdir(self.path):
			raise Exception(
				f'Passed file {self.path} is not a directory file.')
		# check if DEBIAN exists
		if not path.exists(f'{self.path}/DEBIAN/control'):
			raise Exception(f'DEBIAN/control does not exist.')
		# get ar command
		ar = cmd_in_path('ar')
		# ensure file exists
		if ar == None:
			raise Exception(
				'Command "ar" is not installed. Please install it in order to use this library.')
		# ensure algorithm is valid
		if self.algorithm is not 'xz' and self.algorithm is not 'gzip' and self.algorithm is not 'bzip2':
			raise Exception(
				f'Invalid algorithm type {self.algorithm}. Valid types are: xz, gzip, bzip2.Default is xz.')
		# ensure compression level is valid
		if self.level < 1 or self.level > 9:
			raise Exception(
				f'Invalid compression level {self.level}. Valid levels are 1-9. Default is 9.')
		# formatted path
		fpath = Path(self.path)
		self.debpath = f'{fpath.name}.deb'
		# tmp dir
		tmp = f'.{fpath.name}.pack.tmp'
		# remove tmp dir if it exists
		if path.exists(tmp):
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

		# this is needed due to a strange issue where xz compression has preset instead of compresslevel.
		if self.algorithm == 'xz':
			# create control archive
			with tarfile.open(f'{tmp}/control.tar.{self.algorithm}', f'w:{self.algorithm}', preset=self.level) as tar:
				tar.add(f'{tmp}/DEBIAN', arcname='/')
				tar.close()

			# create data archive
			with tarfile.open(f'{tmp}/data.tar.{self.algorithm}', f'w:{self.algorithm}', preset=self.level) as tar:
				tar.add(f'{tmp}/FILESYSTEM', arcname='/')
				tar.close()
		else:
			# create control archive
			with tarfile.open(f'{tmp}/control.tar.{self.algorithm}', f'w:{self.algorithm}', compresslevel=self.level) as tar:
				tar.add(f'{tmp}/DEBIAN', arcname='/')
				tar.close()

			# create data archive
			with tarfile.open(f'{tmp}/data.tar.{self.algorithm}', f'w:{self.algorithm}', compresslevel=self.level) as tar:
				tar.add(f'{tmp}/FILESYSTEM', arcname='/')
				tar.close()

		# create binary
		with open(f'{tmp}/debian-binary', 'w') as f:
			f.write('2.0')
			f.close()

		# delete paths
		rmtree(f'{tmp}/DEBIAN')
		rmtree(f'{tmp}/FILESYSTEM')

		# create deb
		system(f'{ar} r {self.debpath} {tmp}/* >/dev/null 2>&1')

		# delete tmp
		rmtree(tmp)
