from dataclasses import dataclass
import json
from pathlib import Path
from typing import List, Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class SettingsExtBase:
	def loadSettingsFile(self, filePath: Path, opTable: 'DAT' = None):
		if filePath and filePath.exists():
			with filePath.open() as f:
				text = f.read()
				settings = json.loads(text or '{}')
		else:
			settings = {}
		pass
	def buildSettings(self):
		pass

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

class UserSettings:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP

	def LoadSettings(self):
		pass

	def SaveSettings(self):
		pass
