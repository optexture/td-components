import os.path

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class PathSetup:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	def BuildPossiblePathsFromParams(self, dat: 'DAT'):
		dat.clear()
		for i in range(1, 5):
			name = getattr(self.ownerComp.par, 'Path{}name'.format(i), None)
			if not name:
				continue
			for j in range(1, 5):
				folder = getattr(self.ownerComp.par, 'Path{}folder{}'.format(i, j), None)
				if folder:
					dat.appendRow([name, folder])

	@staticmethod
	def PreparePathTable(outDat: 'DAT', inDat: 'DAT'):
		paths = {}
		for cells in inDat.rows():
			name = cells[0].val
			if name in paths:
				continue
			path = cells[1].val
			if os.path.exists(path):
				paths[name] = path
		outDat.clear()
		for name, path in paths.items():
			outDat.appendRow([name, path])

	def ApplyPaths(self):
		table = self.ownerComp.op('path_table')  # type: DAT
		newPaths = {name.val: path.val for name, path in table.rows()}
		missingPathNames = [name for name in project.paths if name not in newPaths]
		for name, path in newPaths.items():
			project.paths[name] = path
		if self.ownerComp.par.Removeotherpaths:
			for name in missingPathNames:
				del project.paths[name]

	@staticmethod
	def ClearAllPaths():
		project.paths.clear()

	@staticmethod
	def BuildCurrentPathsTable(dat: 'DAT'):
		dat.clear()
		for name, path in project.paths.items():
			dat.appendRow([name, path])
