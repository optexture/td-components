# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ModulatedValue:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	# def BuildValueSettings(self, dat: 'DAT'):
	# 	dat.clear()
	# 	dat.appendRow(['index', 'name', 'valuePar', 'modValuePar'])
	# 	for i in range(1, 5):
	# 		name = getattr(self.ownerComp.par, 'Valuename{}'.format(i))
	# 		if not name:
	# 			continue
	# 		dat.appendRow([
	# 			i,
	# 			name,
	# 			'Value{}'.format(i),
	# 			'Modvalue{}'.format(i),
	# 		])
