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

	def _BuildSettings(self):
		settings = self.statePar.Settings.eval() or {}
		for par in self.state.pars('Name'):
			if par.eval() in (None, ''):
				continue
			settings[par.name] = par.eval()
		return settings

	def SaveSettings(self):
		if not self.statePar.Rootfolder or not self.ownerComp.par.Settingsfile:
			raise Exception('No workspace selected')
		folderPath = Path(self.statePar.Rootfolder.eval())
		settings = self.statePar.Settings.eval() or {}
		for par in self.state.pars('Name'):
			if par.eval() in (None, ''):
				continue
			settings[par.name] = par.eval()
		folderPath.mkdir(parents=True, exist_ok=True)
		jsonDat = self.ownerComp.op('settings_json')
		jsonDat.text = json.dumps(settings, indent='  ')
		jsonDat.par.writepulse.pulse()
