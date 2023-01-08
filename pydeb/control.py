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
			match key:
				case 'Package':
					self.package = value
				case 'Name':
					self.name = value
				case 'Version':
					self.version = value
				case 'Author':
					self.author = value
				case 'Maintainer':
					self.maintainer = value
				case 'Description':
					self.description = value
				case 'Architecture':
					self.architecture = value
				case 'Depends':
					self.depends = value
				case 'Section':
					self.section = value
				case 'Icon':
					self.icon = value
				case 'Depiction':
					self.depiction = value
				case 'SileoDepiction':
					self.sileodepiction = value