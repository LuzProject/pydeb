# module imports
import tarfile
from os import listdir, mkdir, path, system
from pathlib import Path
from shutil import copytree, rmtree

# local imports
from .utils import cmd_in_path

class Pack:
	def __init__(self, path: str):
		# path to pack
		self.path = path
		self.__pack()
		
	def __pack(self):
		# check if path exists
		if not path.exists(self.path):
			raise Exception(f'Passed file {self.path} does not exist.')
		# check if path is correct
		if not path.isdir(self.path):
			raise Exception(f'Passed file {self.path} is not a directory file.')
		# check if DEBIAN exists
		if not path.exists(f'{self.path}/DEBIAN/control'):
			raise Exception(f'DEBIAN/control does not exist.')
		# get ar command
		ar = cmd_in_path('ar')
		# ensure file exists
		if ar == None:
			raise Exception('Command "ar" is not installed. Please install it in order to use this library.')
		# formatted path
		fpath = Path(self.path)
		# tmp dir
		tmp = f'.{fpath.name}.pack.tmp'
		# loop through files
		for f in listdir(self.path):
			if f == 'DEBIAN':
				copytree(f'{self.path}/{f}', f'{tmp}/DEBIAN')
			else:
				copytree(f'{self.path}/{f}', f'{tmp}/FILESYSTEM/{f}')
				
		# create control archive
		with tarfile.open(f'{tmp}/control.tar.xz', 'w:xz') as tar:
			tar.add(f'{tmp}/DEBIAN', arcname='/')
			tar.close()
			
		# create data archive
		with tarfile.open(f'{tmp}/data.tar.xz', 'w:xz') as tar:
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
		system(f'{ar} r {fpath.name}.deb {tmp}/*')
		
		# delete tmp
		rmtree(tmp)
