class Control:
	def __init__(self, control: str):
		# raw control
		self.raw = control
		
		# bundle id
		self.package: str
		
		# name
		self.name: str
		
		# version
		self.version: str
		
		# author
		self.author: str
		
		# maintainer
		self.maintainer: str
		
		# desc
		self.description: str
		
		# arch
		self.architecture: str
		
		# depends
		self.depends: str
		
		# section
		self.section: str
		
		# icon
		self.icon: str
		
		# depiction
		self.depiction: str
		
		# sileo depiction
		self.sileodepiction: str
		
		# assign
		self.__assign(control)
	

	def __assign(self, control: str):
		last = ''
		# split control by line
		for line in control.splitlines():
			# split by value and key
			key = ''
			value = ''
			# check and make sure no multiline funny business is going on
			if len(line.split(': ')) == 1:
				key = last
				value = line
			else:
				key = line.split(': ')[0]
				value = line.split(': ')[1]
				last = key
			# match statement
			if key == 'Package':
				self.package = value
			elif key == 'Name':
				self.name = value
			elif key == 'Version':
				self.version = value
			elif key == 'Author':
				self.author = value
			elif key == 'Maintainer':
				self.maintainer = value
			elif key == 'Description':
				self.description = value
			elif key == 'Architecture':
				self.architecture = value
			elif key == 'Depends':
				self.depends = value
			elif key == 'Section':
				self.section = value
			elif key == 'Icon':
				self.icon = value
			elif key == 'Depiction':
				self.depiction = value
			elif key == 'SileoDepiction':
				self.sileodepiction = value
    