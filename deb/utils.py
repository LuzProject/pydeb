# module imports
from os import path, walk
from shutil import which
from typing import Union


def get_filepaths(directory):
	file_paths = []
	
	for root, directories, files in walk(directory):
		for filename in files:
			filepath = path.join(root.replace(directory, '') + '/' + filename)
			file_paths.append(filepath)

	return file_paths

def cmd_in_path(cmd: str) -> Union[None, str]:
	'''Check if command is in PATH'''
	path = which(cmd)
	
	if path is None:
		return None
	
	return path