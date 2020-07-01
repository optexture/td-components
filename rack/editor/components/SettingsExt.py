from abc import ABC, abstractmethod
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, List, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

try:
	from TDStoreTools import DependList, DependDict
except ImportError:
	from _stubs.TDStoreTools import DependList, DependDict

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
			json.dump(settings, f, indent='  ', cls=_CustomEncoder)
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
				if self._isEligible(par):
					pars.append(par)
		if self.pages:
			for page in o.customPages:
				if page.name in self.pages:
					for par in page.pars:
						if self._isEligible(par):
							pars.append(par)
		return pars

	@staticmethod
	def _isEligible(par: 'Par'):
		if not par.enable or par.readOnly or not par.isCustom:
			return False
		if par.label.startswith('-'):
			return False
		if par.isPulse:
			return False
		return True

	def buildSettings(self):
		settings = {}
		for par in self._getParams():
			if par.mode == ParMode.CONSTANT:
				settings[par.name] = par.eval()
			elif par.mode == ParMode.EXPRESSION:
				settings[par.name] = {'$': par.expr}
		return settings

	def applySettings(self, settings: dict):
		for par in self._getParams():
			if settings and par.name in settings:
				val = settings[par.name]
				if isinstance(val, dict) and '$' in val:
					par.expr = val['$']
				else:
					par.val = val
			else:
				par.val = par.default

class UserSettings(SettingsExtBase):
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP

	def getSettingsOps(self) -> List['SettingsOp']:
		return [SettingsOp('settings', op=self.ownerComp, pages=['Settings'])]

	def buildSettings(self):
		settings = super().buildSettings()
		settings['recorderPresets'] = self.getRecorderPresets()
		return settings

	def getRecorderPresets(self):
		recorderPresets = self.getRecorderPresetsComp()
		if not recorderPresets:
			return {}
		return {
			'Banks': recorderPresets.Banks
		}

	def setRecorderPresets(self, settings):
		recorderPresets = self.getRecorderPresetsComp()
		if not recorderPresets:
			return
		recorderPresets.Banks = (settings and settings.get('Banks')) or []

	def applySettings(self, settings: dict):
		super().applySettings(settings)
		self.setRecorderPresets(settings.get('recorderPresets'))

	def getRecorderPresetsComp(self) -> 'Any':
		return self.ownerComp.par.Recorderpresetscomp.eval()

	def getSettingsPath(self):
		return Path(self.ownerComp.par.Usersettingsfile.eval())

	def LoadSettings(self):
		self.loadSettingsFile(self.getSettingsPath())

	def Loadsettings(self, par):
		self.LoadSettings()

	def SaveSettings(self):
		self.saveSettingsFile(self.getSettingsPath())

	def Savesettings(self, par):
		self.SaveSettings()

	def RecentWorkspaces(self) -> List[str]:
		return [
			path
			for path in self.ownerComp.par.Recentworkspaces.eval() or []
			if path and path != '.'
		]

	def AddRecentWorkspace(self, workspaceSettingsFile: str):
		workspaceSettingsFile = tdu.collapsePath(str(Path(workspaceSettingsFile).as_posix()))
		workspaces = self.RecentWorkspaces()
		if workspaceSettingsFile in workspaces:
			workspaces.remove(workspaceSettingsFile)
		workspaces.insert(0, workspaceSettingsFile)
		self.ownerComp.par.Recentworkspaces.val = workspaces
		self.SaveSettings()

class _CustomEncoder(json.JSONEncoder):
	def default(self, o):
		if isinstance(o, (DependList, DependDict)):
			return o.getRaw()
		return o
