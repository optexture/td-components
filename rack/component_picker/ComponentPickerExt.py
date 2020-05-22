
# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ComponentPicker:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
	
	def BuildComponentTable(self, dat: 'DAT', files: 'DAT'):
		dat.clear()
		dat.appendRow(['relpath', 'name', 'toxfullpath', 'thumbfullpath'])

		pass
