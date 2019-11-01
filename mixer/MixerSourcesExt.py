from dataclasses import dataclass
import dataclasses
from typing import Any, Dict, Iterable, List, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class SourceTrack:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	@property
	def SourcesTable(self):
		o = self.ownerComp.par.Sources.eval()
		if not o:
			return None
		if o.isDAT:
			return o
		if not o.isCOMP:
			return None
		if hasattr(o.par, 'Sourcetable'):
			src = o.par.Sourcetable.eval()
			if src and src.isDAT:
				return src
		src = o.op('sources')
		if src and src.isDAT:
			return src
		return None

	@staticmethod
	def PrepareOpSources(dat: 'DAT', paths: Iterable[Union[str, 'OP']]):
		_prepareOpSources(dat, paths)

	@property
	def SourceButtonLabels(self):
		wrapcount = int(self.ownerComp.par.Sourcebuttonwrapchars)
		sources = self.ownerComp.op('sources')  # type: DAT
		labels = [
			str(sources[i, 'label'] or sources[i, 'shortName'] or sources[i, 'legalName'] or '-')
			for i in range(1, sources.numRows)
		]
		if wrapcount <= 0:
			return labels
		return [_wrapString(s, wrapcount) for s in labels]

def _wrapString(s, wraplen):
	strlen = len(s)
	if strlen <= wraplen:
		return s
	return r'\n'.join([s[i:i + wraplen] for i in range(0, strlen, wraplen)])

class MixerSources:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	@staticmethod
	def PrepareOpSources(dat: 'DAT', paths: Iterable[Union[str, 'OP']]):
		_prepareOpSources(dat, paths)

def _prepareOpSources(dat: 'DAT', paths: Iterable[Union[str, 'OP']]):
	dat.clear()
	dat.appendRow(_sourceColumns)
	if not paths:
		return
	srcops = ops(*paths)
	for o in srcops:
		src = _Source(
			path=o.path,
			legalName=o.name,
			type='OP',
		)
		src.label = _firstStringPar(o, 'Label', 'Uilabel', 'Name') or o.name
		src.shortName = _firstStringPar(o, 'Shortlabel', 'Shortname') or src.label
		if o.isTOP:
			src.videoPath = o.path
			src.compPath = o.parent().path
		elif o.isCOMP:
			vidop = _getCompVideoSource(o)
			src.videoPath = vidop.path if vidop else None
			src.compPath = o.path
		else:
			continue
		src.appendToRow(dat)

def _getCompVideoSource(o):
	if o and o.isCOMP:
		for pattern in [
			'out1',
			'video_out',
			'*_out',
			'out*',
			'*out',
		]:
			for out in o.ops(pattern):
				if out.isTOP:
					return out
			pass
	return None

def _firstStringPar(o, *names):
	if not o:
		return None
	for par in o.pars(*names):
		if par:
			return par.eval()

@dataclass
class _Source:
	path: str = None
	legalName: str = None
	sourceName: str = None
	shortName: str = None
	label: str = None
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
		if 'extraFields' in data:
			del data['extraFields']
		if self.extraFields:
			data.update(self.extraFields)
		addDictRow(dat, data)

_sourceColumns = [f.name for f in dataclasses.fields(_Source) if f.name != 'extraFields']


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
