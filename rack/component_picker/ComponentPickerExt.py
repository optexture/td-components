import re
from datetime import datetime

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ComponentPicker:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.statePar = ownerComp.op('iparpicker').par
	
	@staticmethod
	def BuildComponentTable(dat: 'DAT', files: 'DAT'):
		dat.clear()
		dat.appendRow(['relpath', 'name', 'modified', 'timestamp', 'tox', 'thumb', 'folder'])
		for i in range(1, files.numRows):
			if files[i, 'extension'] != 'tox':
				continue
			relPath = files[i, 'relpath'].val
			thumbPath = _findThumbPath(files, relPath)
			timestamp = int(files[i, 'datemodified'] or 0)
			if not timestamp:
				modified = ''
			else:
				modified = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
			folder = files[i, 'folder'].val
			dat.appendRow([
				relPath,
				re.sub(r'([\w_ ]+)/\1\.tox$', r'\1', relPath),
				modified,
				timestamp,
				tdu.collapsePath(files[i, 'path'].val),
				tdu.collapsePath(thumbPath) if thumbPath else '',
				tdu.collapsePath(folder) if folder else '',
			])

	def UpdateListFromPar(self, par: 'Par' = None):
		if par is None:
			par = self.ownerComp.par.Selectedcomp
		listWidget = self.ownerComp.op('component_list')
		if not par:
			index = None
		else:
			cell = self.ownerComp.op('component_table')[par.eval(), 'relpath']
			index = cell.row if cell is not None else None
		listWidget.par.Selectedrows = index if index is not None else ''

	def Refreshpulse(self, par):
		self.ownerComp.op('folder').par.refreshpulse.pulse()

	def Selectedcomp(self, par, val, prev):
		self.UpdateListFromPar(par)

	def OnSelectRow(self, info: dict):
		rowData = info.get('rowData') or {}
		rowObject = rowData.get('rowObject') or {}
		self.ownerComp.par.Selectedcomp = rowObject.get('relpath') or ''

	def OnListRollover(self, info: dict):
		self.statePar.Hoverrow = info.get('row', -1)

def _findThumbPath(files: 'DAT', toxPath: str):
	toxPathBase = re.sub('.tox$', '', toxPath)
	for path in files.col('relpath')[1:]:
		extension = files[path, 'extension'].val
		if extension not in tdu.fileTypes['image']:
			continue
		basePath = re.sub('.' + extension, '', path.val)
		if basePath == toxPathBase:
			return files[path.row, 'path'].val
		if basePath == toxPathBase.rsplit('/', maxsplit=1)[0] + '/thumb':
			return files[path.row, 'path'].val

def OnStart():
	run(f'op({parent.picker.path!r}).UpdateListFromPar()', delayFrames=2)

def OnCreate():
	OnStart()
