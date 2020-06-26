from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from pathlib import Path
from typing import List, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class SettingsExtBase(ABC):
	@abstractmethod
	def getSettingsOps(self) -> List['SettingsOp']:
		pass

	def loadSettingsFile(self, filePath: Path):
		if filePath and filePath.exists():
			with filePath.open('r') as f:
				text = f.read()
				settings = json.loads(text or '{}')
		else:
			settings = {}
		self.applySettings(settings)

	def saveSettingsFile(self, filePath: Path):
		settings = self.buildSettings()
		with filePath.open('w') as f:
			json.dump(settings, f, indent='  ')
		return settings

	def applySettings(self, settings: dict):
		settingsOps = self.getSettingsOps()
		for settingsOp in settingsOps:
			settingsOp.applySettings(settings.get(settingsOp.name))

	def buildSettings(self):
		settingsOps = self.getSettingsOps()
		settings = {}
		for settingsOp in settingsOps:
			settings[settingsOp.name] = settingsOp.buildSettings()
		return settings

@dataclass
class SettingsOp:
	name: str
	op: Optional['OP'] = None
	# note that this is an OR combination, meaning that it is all the params that
	# are listed in `paramNames` plus all the params in all the pages listed in `paramPages`
	params: Optional[List[str]] = None
	pages: Optional[List[str]] = None

	@classmethod
	def fromDatRow(cls, dat: 'DAT', row):
		return cls(
			name=str(dat[row, 'name']),
			params=str(dat[row, 'params'] or '').split(' '),
			pages=str(dat[row, 'paramPages'] or '').split(' '),
		)

	def _getParams(self):
		if self.op:
			o = self.op
		else:
			o = getattr(iop, self.name, None)
		if not o:
			return []
		pars = []
		if self.params:
			for par in o.pars(*self.params):
				if par.enable and not par.readOnly and not par.label.startswith('-') and par.isCustom:
					pars.append(par)
		if self.pages:
			for page in o.customPages:
				if page.name in self.pages:
					for par in page.pars:
						if par.enable and not par.readOnly and not par.label.startswith('-') and par.isCustom:
							pars.append(par)
		return pars

	def buildSettings(self):
		return {
			par.name: par.eval()
			for par in self._getParams()
		}

	def applySettings(self, settings: dict):
		for par in self._getParams():
			if settings and par.name in settings:
				par.val = settings[par.name]
			else:
				par.val = par.default

class UserSettings(SettingsExtBase):
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP

	def getSettingsOps(self) -> List['SettingsOp']:
		return [SettingsOp('settings', pages=['Settings'])]

	def getSettingsPath(self):
		return Path(self.ownerComp.par.Usersettingsfile.eval())

	def LoadSettings(self):
		self.loadSettingsFile(self.getSettingsPath())

	def SaveSettings(self):
		self.loadSettingsFile(self.getSettingsPath())

	def RecentWorkspaces(self) -> List[str]:
		return self.ownerComp.par.Recentworkspaces.eval() or []

	def AddRecentWorkspace(self, workspaceSettingsFile: str):
		workspaces = self.RecentWorkspaces()
		if workspaceSettingsFile in workspaces:
			workspaces.remove(workspaceSettingsFile)
		workspaces.insert(0, workspaceSettingsFile)
		self.ownerComp.par.Recentworkspaces.val = workspaces
		self.SaveSettings()
