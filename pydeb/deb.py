# module imports
from os import getcwd, listdir, mkdir, path, remove, system
from pathlib import Path
from shutil import rmtree
import xtarfile as tarfile

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
		self.control = Control(open(f'{tmp}/DEBIAN/control').read())
		
		# filepaths
		self.filepaths = {'root': [], 'control': []}
		
		# assign filepaths
		for file in get_filepaths(tmp):
			# if file starts with /control, add it to 'control'
			if file.startswith('/DEBIAN'):
				self.filepaths['control'].append(file.replace('/DEBIAN/', ''))
			else:
				self.filepaths['root'].append(file.replace('/data', ''))
		
		# get contents of scripts
		self.scripts = {}
		
		for f in self.filepaths.get('control'):
			if f == '': continue
			self.scripts[f.replace('/', '')] = open(f'{tmp}/DEBIAN/{f}').read()
		
		if remove_file: rmtree(tmp)

	def __extract(self) -> str:
		# set file var
		file = self.file
		# check if file exists
		if not path.exists(file):
			raise Exception(f'Passed file {file} does not exist.')
		# check if file is correct
		if not file.endswith('.deb'):
			raise Exception(f'Passed file {file} is not a deb file.')
		# filename
		filename = Path(file).name
		# set path
		if self.rmfile:
			self.xpath = f'./.{filename}.tmp'
		else:
			self.xpath = f'./{filename.replace(".deb", "")}'
		# get full path
		fpath = f'{file if file.startswith("/") else getcwd() + "/" + file}'
		# get ar command
		ar = cmd_in_path('ar')
		# ensure file exists
		if ar == None:
			raise Exception('Command "ar" is not installed. Please install it in order to use this library.')
        # if tmp dir exists, remove it
		if path.exists(self.xpath):
			rmtree(self.xpath)
		# make tmp dir
		mkdir(self.xpath)
		# extract deb
		system(f'cd {self.xpath} && ar x {fpath}')
		# remove all files except control and data
		for file in listdir(self.xpath):
			if not file.startswith('control.') and not file.startswith('data.'):
				remove(f'{self.xpath}/{file}')
			else:
				filename = 'DEBIAN' if file.startswith('control.') else ''
				# make sure file is a tar
				if 'tar' not in file:
					raise Exception(f'Unknown archive format. ({file.replace("control.", "").replace("data.", "")})')
				
				# open file in read mode
				with tarfile.open(f'{self.xpath}/{file}', 'r') as file_obj:
					# extract all files
					file_obj.extractall(f'{self.xpath}/{filename}')
					file_obj.close()
				
				# remove tar
				remove(f'{self.xpath}/{file}')

		# return path that we extracted to
		return self.xpath