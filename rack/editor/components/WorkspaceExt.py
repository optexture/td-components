import json
from pathlib import Path
from typing import List, Optional

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
		self._ApplySettingsToOp(
			self.ownerComp,
			settings.get('workspace') or {},
			paramNames=[],
			paramPages=['Settings'],
		)
		opTable = self.ownerComp.par.Settingsoptable.eval()  # type: DAT
		if opTable:
			for i in range(1, opTable.numRows):
				opName = opTable[i, 'name'].val
				self._ApplySettingsToOp(
					getattr(iop, opName, None),
					settings.get(opName) or {},
					(opTable[i, 'params'].val or '').split(' '),
					(opTable[i, 'paramPages'].val or '').split(' '))
		self.ownerComp.par.Name = self.ownerComp.par.Name or folderPath.name
		self.ownerComp.par.Settings = settings

	@staticmethod
	def _ApplySettingsToOp(
			o: Optional[OP],
			settings: dict,
			paramNames: List[str],
			paramPages: List[str]):
		pars = _getOpParams(o, paramNames, paramPages)
		for par in pars:
			if par.name in settings:
				par.val = settings[par.name]
			else:
				par.val = par.default

	def _BuildSettings(self):
		settings = self.ownerComp.par.Settings.eval() or {}
		settings['workspace'] = self._BuildSettingsForOp(
			self.ownerComp,
			paramNames=[],
			paramPages=['Settings'],
		)
		opTable = self.ownerComp.par.Settingsoptable.eval()  # type: DAT
		if opTable:
			for i in range(1, opTable.numRows):
				opName = opTable[i, 'name'].val
				opSettings = self._BuildSettingsForOp(
					getattr(iop, opName, None),
					(opTable[i, 'params'].val or '').split(' '),
					(opTable[i, 'paramPages'].val or '').split(' '))
				settings[opName] = opSettings
		return settings

	@staticmethod
	def _BuildSettingsForOp(
			o: Optional[OP],
			paramNames: List[str],
			paramPages: List[str]):
		settings = {}
		for par in _getOpParams(o, paramNames, paramPages):
			settings[par.name] = par.eval()
		return settings

	def SaveSettings(self):
		if not self.statePar.Rootfolder or not self.ownerComp.par.Settingsfile:
			raise Exception('No workspace selected')
		folderPath = Path(self.statePar.Rootfolder.eval())
		settings = self._BuildSettings()
		self.ownerComp.par.Settings = settings
		settingsJson = json.dumps(settings, indent='  ')
		folderPath.mkdir(parents=True, exist_ok=True)
		jsonDat = self.ownerComp.op('settings_json')
		jsonDat.text = settingsJson
		jsonDat.par.writepulse.pulse()
		print(f'Saved workspace settings to {jsonDat.par.file}')

def _getOpParams(o: Optional[OP], paramNames: List[str], paramPages: List[str]):
	if not o:
		return []
	pars = []
	if paramNames:
		for par in o.pars(*paramNames):
			if par.enable and not par.readOnly and not par.label.startswith('-'):
				pars.append(par)
	if paramPages:
		for page in o.customPages:
			if page.name in paramPages:
				for par in page.pars:
					if par.enable and not par.readOnly and not par.label.startswith('-'):
						pars.append(par)
	return pars
