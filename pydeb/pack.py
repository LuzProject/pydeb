# module imports
from multiprocessing.pool import ThreadPool
from os import listdir, makedirs, scandir
from pathlib import Path
from shutil import copytree, rmtree
from time import time

# local imports
from .control import Control
from .utils import resolve_path
from .archives.tar import TAR
from .archives.constrictor.ar import ARWriter


class Pack:
	def __init__(self, path: Path, algorithm: str = 'xz', compression_level: int = 9, outdir: str = './'):
		# outdir
		self.outdir = outdir

		if not resolve_path(outdir).exists():
			makedirs(outdir)
		
		# check if path is Path
		if type(path) is not Path: path = resolve_path(path)
		
		# tar
		self.tar = TAR(algorithm, compression_level)

		# path to pack
		self.path = path

		# path of deb
		self.debpath = ''
		self.__pack()

	def __get_dir_size(self, path='.'):
		total = 0
		with scandir(path) as it:
			for entry in it:
				if entry.is_file():
					total += entry.stat().st_size
				elif entry.is_dir():
					total += self.__get_dir_size(entry.path)
		return total

	def __compress_object(self, tmp, dir_name):
		archive_name = 'data.tar'
		if dir_name == 'DEBIAN': archive_name = 'control.tar'
		self.tar.compress_directory(f'{tmp}/{dir_name}', archive_name)

	
	def __remove_unwanted_paths(self, path):
		with scandir(path) as it:
			for entry in it:
				if entry.is_file():
					if entry.path.endswith('.DS_Store') or entry.path.endswith('.gitignore'):
						rmtree(entry.path)
				elif entry.is_dir():
					self.__remove_unwanted_paths(entry.path)


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
			self.debpath = f'{self.outdir}{control.package}_{control.version}_{control.architecture}.deb'
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

		
		# get installed size
		installed_size = int(round((self.__get_dir_size(f'{tmp}/FILESYSTEM') / 1024), 0))
		with open(f'{tmp}/DEBIAN/control', 'a') as f:
			f.write(f'Installed-Size: {installed_size}\n')
			f.close()

		with ThreadPool() as pool:
			pool.starmap(self.__compress_object, [(tmp, 'DEBIAN'), (tmp, 'FILESYSTEM')])
			pool.map(self.__remove_unwanted_paths, [f'{tmp}/FILESYSTEM', f'{tmp}/DEBIAN'])

		# create binary
		with open(f'{tmp}/debian-binary', 'w') as f:
			f.write('2.0\n')
			f.close()

		# delete paths
		rmtree(f'{tmp}/DEBIAN')
		rmtree(f'{tmp}/FILESYSTEM')

		# create deb
		with open(self.debpath, 'wb') as ar_fp:
			ar_writer = ARWriter(ar_fp)

			ar_writer.archive_text("debian-binary", f"2.0\n", int(time()), 0, 0, 0o644)
			ar_writer.archive_file(f'{resolve_path(f"{tmp}/control.tar.*")[0]}', int(time()), 0, 0, 0o644)
			ar_writer.archive_file(f'{resolve_path(f"{tmp}/data.tar.*")[0]}', int(time()), 0, 0, 0o644)

		# delete tmp
		rmtree(tmp)
