from dataclasses import dataclass
import dataclasses
from typing import Any, Dict

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class MixerSourcesExt:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

def PrepareOpSources(indat: 'DAT', dat: 'DAT'):
	dat.clear()
	dat.appendRow(_sourceColumns)
	if not indat:
		return

	pass

@dataclass
class Source:
	legalName: str = None
	sourceName: str = None
	path: str = None
	shortName: str = None
	compPath: str = None
	videoPath: str = None
	type: str = None
	deviceName: str = None
	active: bool = None
	streaming: bool = None
	fps: int = None
	url: str = None
	extraFields: Dict[str, Any] = None

	def appendToRow(self, dat: 'DAT'):
		data = dict(dataclasses.asdict(self))
		if self.extraFields:
			data.update(self.extraFields)
		addDictRow(dat, data)

_sourceColumns = dataclasses.fields(Source)

NULL_PLACEHOLDER = '_'

def formatValue(val, nonevalue=NULL_PLACEHOLDER):
	if isinstance(val, str):
		return val
	if val is None:
		return nonevalue
	if isinstance(val, bool):
		return str(int(val))
	if isinstance(val, float) and int(val) == val:
		return str(int(val))
	return str(val)

def addDictRow(dat, obj: Dict[str, Any]):
	r = dat.numRows
	dat.appendRow([])
	setDictRow(dat, r, obj)

def setDictRow(dat, rowkey: Union[str, int], obj: Dict[str, Any], clearmissing=False):
	for key, val in obj.items():
		dat[rowkey, key] = formatValue(val, nonevalue='')
	if clearmissing:
		for col in dat.row(0):
			if col.val not in obj:
				col.val = ''
