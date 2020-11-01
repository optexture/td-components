from pathlib import Path
from typing import List, Optional
from .SettingsExt import SettingsOp, SettingsExtBase

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from typing import Any
	iop.workspaceState = COMP()
	ipar.workspaceState = Any()

class Workspace(SettingsExtBase):
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP

	def getSettingsOps(self) -> List['SettingsOp']:
		settingsOps = [
			self.workspaceSettingsOp()
		]
		opTable = self.ownerComp.par.Settingsoptable.eval()  # type: DAT
		if opTable:
			for i in range(1, opTable.numRows):
				settingsOps.append(SettingsOp.fromDatRow(opTable, i))
		return settingsOps

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

	def OpenWorkspace(self, fileOrFolder: str):
		path = Path(fileOrFolder)
		if path.is_dir():
			self.LoadWorkspaceFolder(path)
		else:
			self.LoadWorkspaceFile(path)

	def workspaceSettingsOp(self):
		return SettingsOp('workspace', op=self.ownerComp, pages=['Settings'])

	def _LoadWorkspace(self, settingsPath: Optional[Path], folderPath: Optional[Path]):
		ipar.workspaceState.Rootfolder = folderPath or ''
		self.ownerComp.par.Settingsfile = settingsPath or ''
		if folderPath is not None:
			folderPath.mkdir(parents=True, exist_ok=True)
		self.loadSettingsFile(settingsPath)
		self.ownerComp.par.Name = self.ownerComp.par.Name or (folderPath.name if folderPath is not None else '')
		self.ownerComp.par.Onworkspaceload.pulse()

	def applySettings(self, settings: dict):
		super().applySettings(settings)
		self.ownerComp.par.Settings = settings

	def UnloadWorkspace(self):
		self._LoadWorkspace(None, None)
		self.ownerComp.par.Onworkspaceunload.pulse()

	def SaveSettings(self):
		if not ipar.workspaceState.Rootfolder or not self.ownerComp.par.Settingsfile:
			raise Exception('No workspace selected')
		folderPath = Path(ipar.workspaceState.Rootfolder.eval())
		folderPath.mkdir(parents=True, exist_ok=True)
		settingsPath = Path(self.ownerComp.par.Settingsfile.eval())
		settings = self.saveSettingsFile(settingsPath)
		self.ownerComp.par.Settings = settings
		print(f'Saved workspace settings to {settingsPath}')
