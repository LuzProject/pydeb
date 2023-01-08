# module imports
import tarfile
from os import getcwd, listdir, mkdir, path, remove, system
from pathlib import Path
from shutil import rmtree

# local imports
from .control import Control
from .utils import cmd_in_path, get_filepaths


class Deb:
	def __init__(self, file: str, remove_file: bool = True):
		# xpath
		self.xpath = ''
		
		# rmfile
		self.rmfile = remove_file
		
		# file path
		self.file = file
		
		# extract
		tmp = self.__extract()
		
		# control
		self.control = Control(open(f'{tmp}/control/control').read())
		
		# filepaths
		self.filepaths = {'root': [], 'control': []}
		
		# assign filepaths
		for file in get_filepaths(tmp):
			# if file starts with /data, add it to 'root'
			if file.startswith('/data'): self.filepaths['root'].append(file.replace('/data', ''))
			# if file starts with /control, add it to 'control'
			if file.startswith('/control'): self.filepaths['control'].append(file.replace('/control/', ''))
		
		# get contents of scripts
		self.scripts = {}
		
		for f in self.filepaths.get('control'):
			if f == '': continue
			self.scripts[f.replace('/', '')] = open(f'{tmp}/control/{f}').read()
		
		if remove_file: rmtree(tmp)

	def __extract(self) -> str:
		# set file var
		file = self.file
		# filename
		filename = Path(file).name
		# set path
		if self.rmfile:
			self.xpath = f'./.{filename}.tmp'
		else:
			self.xpath = f'./{filename.replace(".deb", "")}'
		# get full path
		path = f'{file if file.startswith("/") else getcwd() + "/" + file}'
		# get ar command
		ar = cmd_in_path('ar')
		# ensure file exists
		if ar == None:
			raise Exception('Command "ar" is not installed. Please install it in order to use this library.')
		# make tmp dir
		mkdir(self.xpath)
		# extract deb
		system(f'cd {self.xpath} && ar x {path}')
		# remove all files except control and data
		for file in listdir(self.xpath):
			if not file.startswith('control.') and not file.startswith('data.'):
				remove(f'{self.xpath}/{file}')
			else:
				# make sure file is a tar
				if 'tar' not in file:
					raise Exception(f'Unknown archive format. ({file.replace("control.", "").replace("data.", "")})')
				
				# open file in read mode
				file_obj = tarfile.open(f'{self.xpath}/{file}', 'r')
				 
				# extract all files
				file_obj.extractall(f'{self.xpath}/{file.split(".")[0]}')
				 
				# close file
				file_obj.close()
				
				# remove tar
				remove(f'{self.xpath}/{file}')

		# return path that we extracted to
		return self.xpath