import json
from pathlib import Path
from typing import List, Optional
from .SettingsExt import SettingsOp

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from typing import Any
	iop.workspaceState = COMP()
	ipar.workspaceState = Any()

class Workspace:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP

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

	def workspaceSettingsOp(self):
		return SettingsOp('workspace', op=self.ownerComp, pages=['Settings'])

	def _LoadWorkspace(self, settingsPath: Optional[Path], folderPath: Optional[Path]):
		ipar.workspaceState.Rootfolder = folderPath or ''
		self.ownerComp.par.Settingsfile = settingsPath or ''
		jsonDat = self.ownerComp.op('settings_json')
		if settingsPath is not None and settingsPath.exists():
			jsonDat.par.loadonstartpulse.pulse()
			settings = json.loads(jsonDat.text or '{}')
		else:
			jsonDat.text = ''
			settings = {}
		if folderPath is not None:
			folderPath.mkdir(parents=True, exist_ok=True)
		self.workspaceSettingsOp().applySettings(settings.get('workspace'))
		opTable = self.ownerComp.par.Settingsoptable.eval()  # type: DAT
		if opTable:
			for i in range(1, opTable.numRows):
				opName = opTable[i, 'name'].val
				SettingsOp.fromDatRow(opTable, i).applySettings(settings.get(opName))
		self.ownerComp.par.Name = self.ownerComp.par.Name or (folderPath.name if folderPath is not None else '')
		self.ownerComp.par.Settings = settings
		self.ownerComp.par.Onworkspaceload.pulse()

	def UnloadWorkspace(self):
		self._LoadWorkspace(None, None)
		self.ownerComp.par.Onworkspaceunload.pulse()

	def _BuildSettings(self):
		settings = self.ownerComp.par.Settings.eval() or {}
		settings['workspace'] = self.workspaceSettingsOp().buildSettings()
		opTable = self.ownerComp.par.Settingsoptable.eval()  # type: DAT
		if opTable:
			for i in range(1, opTable.numRows):
				opName = opTable[i, 'name'].val
				settings[opName] = SettingsOp.fromDatRow(opTable, i).buildSettings()
		return settings

	def SaveSettings(self):
		if not ipar.workspaceState.Rootfolder or not self.ownerComp.par.Settingsfile:
			raise Exception('No workspace selected')
		folderPath = Path(ipar.workspaceState.Rootfolder.eval())
		settings = self._BuildSettings()
		self.ownerComp.par.Settings = settings
		settingsJson = json.dumps(settings, indent='  ')
		folderPath.mkdir(parents=True, exist_ok=True)
		jsonDat = self.ownerComp.op('settings_json')
		jsonDat.text = settingsJson
		jsonDat.par.writepulse.pulse()
		print(f'Saved workspace settings to {jsonDat.par.file}')
