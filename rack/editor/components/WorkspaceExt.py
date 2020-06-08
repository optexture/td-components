import json
from pathlib import Path

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from typing import Any
	iop.workspaceState = COMP()
	ipar.workspaceState = Any()

class Workspace:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.statePar = ipar.workspaceState

	def LoadWorkspace(self, file: str):
		filePath = Path(file)
		if not filePath.exists():
			# TODO: handle missing file by creating a new one
			if filePath.name.endswith('.json'):
				folderPath = filePath.parent
				settingsPath = filePath
			elif filePath.suffix:
				raise Exception(f'Unsupported workspace file type: {file}')
			else:
				folderPath = filePath
				settingsPath = filePath / 'workspace.json'
		elif filePath.is_dir():
			folderPath = filePath
			settingsPath = filePath / 'workspace.json'
		else:
			settingsPath = filePath
			folderPath = settingsPath.parent
		pass

	def LoadWorkspaceFolder(self, path: str):
		folderPath = Path(path)
		self._LoadWorkspace(
			folderPath / 'workspace.json',
			folderPath)

	def _LoadWorkspace(self, settingsPath: Path, folderPath: Path):
		self.statePar.Rootfolder = folderPath
		self.statePar.Settingsfile = settingsPath
		
		pass

	def SaveSettings(self, saveAs=None):
		pass

	def _GetSettings(self):
		return {
			par.name: par.eval()
			for par in self.ownerComp.pars('Name')
		}

	def GetSettingsJson(self):
		settings = self._GetSettings()
		return json.dumps(settings, indent='  ')

	def SetSettings(self, settings: dict):
		settings = settings or {}

		pass

def _tableToDict(dat: 'DAT'):
	return {
		name.val: _parseValue(value.val)
		for name, value in dat.rows()
	}


NULL_PLACEHOLDER = ''

def _parseValue(val, nonevalue=NULL_PLACEHOLDER):
	if val is None or val == nonevalue:
		return None
	if val == '' or isinstance(val, (int, float)):
		return val
	try:
		# noinspection PyTypeChecker
		parsed = float(val)
		if int(parsed) == parsed:
			return int(parsed)
		return parsed
	except ValueError:
		return val

def _formatValue(val, nonevalue=NULL_PLACEHOLDER):
	if isinstance(val, str):
		return val
	if val is None:
		return nonevalue
	if isinstance(val, float) and int(val) == val:
		return str(int(val))
	return str(val)