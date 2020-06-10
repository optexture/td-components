import json
from pathlib import Path
from typing import List

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
		self.state = iop.workspaceState
		self.statePar = ipar.workspaceState

	def PromptLoadWorkspaceFile(self):
		path = ui.chooseFile(load=True, fileTypes=['json'], title='Open Workspace File')
		if path:
			self.LoadWorkspaceFile(path)

	def PromptLoadWorkspaceFolder(self):
		path = ui.chooseFolder(title='Open Workspace Folder')
		if path:
			self.LoadWorkspaceFolder(path)

	def LoadWorkspaceFile(self, file: str):
		filePath = Path(file)
		self._LoadWorkspace(
			filePath,
			filePath.parent)

	def LoadWorkspaceFolder(self, path: str):
		folderPath = Path(path)
		self._LoadWorkspace(
			folderPath / 'workspace.json',
			folderPath)

	def _LoadWorkspace(self, settingsPath: Path, folderPath: Path):
		self.statePar.Rootfolder = folderPath
		self.ownerComp.par.Settingsfile = settingsPath
		if settingsPath.exists():
			jsonDat = self.ownerComp.op('settings_json')
			jsonDat.par.loadonstartpulse.pulse()
			settings = json.loads(jsonDat.text or '{}')
		else:
			settings = {}
		folderPath.mkdir(parents=True, exist_ok=True)
		self.statePar.Settings = settings
		self.statePar.Name = settings.get('Name') or folderPath.name
		self.statePar.Subcomptags = settings.get('Subcomptags') or ''
		opTable = self.ownerComp.par.Settingsoptable.eval()  # type: DAT
		if opTable:
			for i in range(1, opTable.numRows):
				opName = opTable[i, 'name'].val
				self._ApplySettingsToOp(
					opName,
					settings.get(opName) or {},
					(opTable[i, 'params'].val or '').split(' '),
					(opTable[i, 'paramPages'].val or '').split(' '))

	@staticmethod
	def _ApplySettingsToOp(
			opName: str,
			settings: dict,
			paramNames: List[str],
			paramPages: List[str]):
		pars = _getOpParams(opName, paramNames, paramPages)
		for par in pars:
			if par.name in settings:
				par.val = settings[par.name]
			else:
				par.val = par.default

	def _BuildSettings(self):
		settings = self.statePar.Settings.eval() or {}
		for par in self.state.pars('Name', 'Subcomptags'):
			settings[par.name] = par.eval()
		opTable = self.ownerComp.par.Settingsoptable.eval()  # type: DAT
		if opTable:
			for i in range(1, opTable.numRows):
				opName = opTable[i, 'name'].val
				opSettings = self._BuildSettingsForOp(
					opName,
					(opTable[i, 'params'].val or '').split(' '),
					(opTable[i, 'paramPages'].val or '').split(' '))
				settings[opName] = opSettings
		return settings

	@staticmethod
	def _BuildSettingsForOp(
			opName: str,
			paramNames: List[str],
			paramPages: List[str]):
		settings = {}
		for par in _getOpParams(opName, paramNames, paramPages):
			settings[par.name] = par.eval()
		return settings

	def SaveSettings(self):
		if not self.statePar.Rootfolder or not self.ownerComp.par.Settingsfile:
			raise Exception('No workspace selected')
		folderPath = Path(self.statePar.Rootfolder.eval())
		settings = self._BuildSettings()
		self.statePar.Settings = settings
		settingsJson = json.dumps(settings, indent='  ')
		folderPath.mkdir(parents=True, exist_ok=True)
		jsonDat = self.ownerComp.op('settings_json')
		jsonDat.text = settingsJson
		jsonDat.par.writepulse.pulse()
		print(f'Saved workspace settings to {jsonDat.par.file}')

def _getOpParams(opName: str, paramNames: List[str], paramPages: List[str]):
	o = getattr(iop, opName, None)  # type: OP
	if not o:
		return []
	pars = []
	for par in o.pars(*paramNames):
		pars.append(par)
	for page in o.customPages:
		if page.name in paramPages:
			pars += page.pars
	return pars
