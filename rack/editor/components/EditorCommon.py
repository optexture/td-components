import dataclasses
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

ValueOrExpr = Union[Any, Dict[str, str]]

@dataclass
class LibrarySpec:
	shortcut: str
	path: str
	allPaths: str

@dataclass
class ComponentSpec:
	name: Optional[str] = None
	label: Optional[str] = None
	tox: Optional[str] = None
	copyOf: Optional[ValueOrExpr] = None
	pars: Optional[Dict[str, ValueOrExpr]] = None

	@classmethod
	def fromDict(cls, d: dict):
		return cls(**d)

	def toDict(self):
		return dataclasses.asdict(self)

	def createComp(self, destination: COMP) -> COMP:
		if self.copyOf:
			if isinstance(self.copyOf, Dict):
				master = destination.evalExpression(self.copyOf['$'])
			else:
				master = destination.op(self.copyOf)
			if not master:
				raise Exception(f'Invalid component spec {self!r}')
			comp = destination.copy(master, name=self.name)
		elif self.tox:
			comp = destination.loadTox(self.tox)
		else:
			raise Exception(f'Invalid component spec {self!r}')
		if self.name:
			comp.name = self.name
		# in case the name need to change for uniqueness, this will store the actual name
		self.name = comp.name
		self.applyParams(comp)
		return comp

	def applyParams(self, comp: COMP):
		if not self.pars:
			return
		for name, val in self.pars.items():
			par = getattr(comp.par, name, None)
			if par is None:
				print(f'Param {name} not found in {comp}')
				continue
			if isinstance(val, dict) and '$' in val:
				par.expr = val['$']
			else:
				par.val = val
