from collections import defaultdict
import datetime
import json
import math
from typing import Any, Dict, Iterable, List, Optional, Union
import sys

# print('common.py loading...')

if False:
	from common.lib._stubs import *


_TimestampFormat = '[%H:%M:%S]'
_PreciseTimestampFormat = '[%H:%M:%S.%f]'

def _LoggerTimestamp():
	return datetime.datetime.now().strftime(
		# _TimestampFormat
		_PreciseTimestampFormat
	)

def Log(msg, file=None):
	print(
		_LoggerTimestamp(),
		msg,
		file=file)
	file.flush()

class IndentedLogger:
	def __init__(self, outfile=None):
		self._indentLevel = 0
		self._indentStr = ''
		self._outFile = outfile

	def _AddIndent(self, amount):
		self._indentLevel += amount
		self._indentStr = '\t' * self._indentLevel

	def Indent(self):
		self._AddIndent(1)

	def Unindent(self):
		self._AddIndent(-1)

	def LogEvent(self, path, opid, event, indentafter=False, unindentbefore=False):
		if unindentbefore:
			self.Unindent()
		if event:
			if not path and not opid:
				Log('%s%s' % (self._indentStr, event), file=self._outFile)
			elif not opid:
				Log('%s%s %s' % (self._indentStr, path or '', event), file=self._outFile)
			else:
				Log('%s[%s] %s %s' % (self._indentStr, opid or '', path or '', event), file=self._outFile)
		if indentafter:
			self.Indent()

	def LogBegin(self, path, opid, event):
		self.LogEvent(path, opid, event, indentafter=True)

	def LogEnd(self, path, opid, event):
		self.LogEvent(path, opid, event, unindentbefore=True)

class _Tee:
	def __init__(self, *files):
		self.files = files

	def write(self, obj):
		for f in self.files:
			f.write(obj)
			# f.flush()  # make the output to be visible immediately

	def flush(self):
		for f in self.files:
			f.flush()

def _InitFileLog():
	f = open(project.name + '-log.txt', mode='a')
	print('\n-----[Initialize Log: {}]-----\n'.format(
		datetime.datetime.now().strftime('%Y.%m.%d %H:%M:%S.%f')), file=f)
	f.flush()
	return IndentedLogger(outfile=_Tee(sys.stdout, f))

#_logger = IndentedLogger()
_logger = _InitFileLog()

class LoggableBase:
	def _GetLogId(self) -> Optional[str]:
		return None

	def _LogEvent(self, event, indentafter=False, unindentbefore=False):
		raise NotImplementedError()

	def _LogBegin(self, event):
		self._LogEvent(event, indentafter=True)

	def _LogEnd(self, event=None):
		self._LogEvent(event, unindentbefore=True)

class ExtensionBase(LoggableBase):
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: op
		self.enablelogging = True
		self.par = ownerComp.par
		self.path = ownerComp.path
		self.op = ownerComp.op
		self.ops = ownerComp.ops
		# trick pycharm
		if False:
			self.storage = {}
			self.docked = []
			self.destroy = ownerComp.destroy

	def _GetLogId(self):
		if not self.ownerComp.valid or not hasattr(self.ownerComp.par, 'opshortcut'):
			return None
		return self.ownerComp.par.opshortcut.eval()

	def _LogEvent(self, event, indentafter=False, unindentbefore=False):
		if self.enablelogging:
			_logger.LogEvent(
				self.ownerComp.path,
				self._GetLogId(),
				event,
				indentafter=indentafter,
				unindentbefore=unindentbefore)

class LoggableSubComponent(LoggableBase):
	def __init__(self, hostobj: LoggableBase, logprefix: str=None):
		self.hostobj = hostobj
		self.logprefix = logprefix if logprefix is not None else type(self).__name__

	def _LogEvent(self, event, indentafter=False, unindentbefore=False):
		if self.hostobj is None:
			return
		if self.logprefix and event:
			event = self.logprefix + ' ' + event
		self.hostobj._LogEvent(event, indentafter=indentafter, unindentbefore=unindentbefore)

def _defaultformatargs(args, kwargs):
	if not args:
		return kwargs or ''
	if not kwargs:
		return args
	return '{} {}'.format(args, kwargs)

def _decoratewithlogging(func, formatargs):
	def wrapper(self: ExtensionBase, *args, **kwargs):
		self._LogBegin('{}({})'.format(func.__name__, formatargs(args, kwargs)))
		try:
			return func(self, *args, **kwargs)
		finally:
			self._LogEnd()
	return wrapper

def loggedmethod(func):
	return _decoratewithlogging(func, _defaultformatargs)

def simpleloggedmethod(func):
	return customloggedmethod(omitargs=True)(func)

def customloggedmethod(
		omitargs: Union[bool, List[str]]=None):
	if not omitargs:
		formatargs = _defaultformatargs
	elif omitargs is True:
		def formatargs(*_):
			return ''
	elif not isinstance(omitargs, (list, tuple, set)):
		raise Exception('Invalid "omitargs" specifier for loggedmethod: {!r}'.format(omitargs))
	else:
		def formatargs(args, kwargs):
			return _defaultformatargs(args, excludekeys(kwargs, omitargs))

	return lambda func: _decoratewithlogging(func, formatargs)

def cleandict(d):
	if not d:
		return None
	return {
		key: val
		for key, val in d.items()
		if not (val is None or (isinstance(val, (str, list, dict, tuple)) and len(val) == 0))
	}

def mergedicts(*parts):
	x = {}
	for part in parts:
		if part:
			x.update(part)
	return x

def excludekeys(d, keys):
	if not d:
		return {}
	return {
		key: val
		for key, val in d.items()
		if key not in keys
	}

def transformkeys(d, fn):
	return {} if not d else {fn(key): val for key, val in d.items()}

def setattrs(obj, **attrs):
	if isinstance(obj, (list, tuple)):
		for o in obj:
			setattrs(o, **attrs)
	else:
		for k, v in attrs.items():
			setattr(obj, k, v)

class BaseDataObject:
	def __init__(self, **attrs):
		self.attrs = attrs

	def ToJsonDict(self) -> dict:
		raise NotImplementedError()

	def __repr__(self):
		return '{}({!r})'.format(self.__class__.__name__, self.ToJsonDict())

	@classmethod
	def FromJsonDict(cls, obj):
		return cls(**obj)

	@classmethod
	def FromJsonDicts(cls, objs: List[Dict]):
		return [cls.FromJsonDict(obj) for obj in objs] if objs else []

	@classmethod
	def FromOptionalJsonDict(cls, obj, default=None):
		return cls.FromJsonDict(obj) if obj else default

	@classmethod
	def FromJsonDictMap(cls, objs: Dict[str, Dict]):
		if not objs:
			return {}
		results = {}
		for key, obj in objs.items():
			val = cls.FromOptionalJsonDict(obj)
			if val:
				results[key] = val
		return results

	@classmethod
	def ToJsonDicts(cls, nodes: 'Iterable[BaseDataObject]'):
		return [n.ToJsonDict() for n in nodes] if nodes else []

	@classmethod
	def ToOptionalJsonDict(cls, obj: 'BaseDataObject'):
		return obj.ToJsonDict() if obj is not None else None

	@classmethod
	def ToJsonDictMap(cls, nodes: 'Dict[str, BaseDataObject]'):
		return {
			path: node.ToJsonDict()
			for path, node in nodes.items()
		} if nodes else {}

	def Clone(self):
		return self.FromJsonDict(self.ToJsonDict())

	@classmethod
	def CloneList(cls, items: 'List[BaseDataObject]'):
		return [item.Clone() for item in (items or [])]

	@classmethod
	def CloneFirst(cls, *items: 'BaseDataObject'):
		if not items:
			return None
		for item in items:
			if item:
				return item
		return None

	def WriteJsonTo(self, filepath):
		obj = self.ToJsonDict()
		with open(filepath, mode='w') as outfile:
			json.dump(obj, outfile, indent='  ')

	@classmethod
	def ReadJsonFrom(cls, filepath):
		with open(filepath, mode='r') as infile:
			obj = json.load(infile)
		return cls.FromJsonDict(obj)

	def AddToTable(self, dat, attrs=None):
		obj = self.ToJsonDict()
		attrs = mergedicts(obj, attrs)
		vals = []
		for col in dat.row(0):
			val = attrs.get(col.val, '')
			if isinstance(val, bool):
				val = 1 if val else 0
			elif isinstance(val, (list, set, tuple)):
				val = ' '.join(val)
			vals.append(val)
		dat.appendRow(vals)

	def UpdateInTable(self, rowid, dat, attrs=None):
		rowcells = dat.row(rowid)
		if not rowcells:
			self.AddToTable(dat, attrs)
		else:
			obj = self.ToJsonDict()
			attrs = mergedicts(obj, attrs)
			for cell in rowcells:
				col = dat[cell.row, 0]
				val = attrs.get(col.val, '')
				if isinstance(val, bool):
					val = 1 if val else 0
				elif isinstance(val, (list, set, tuple)):
					val = ' '.join(val)
				cell.val = val

def addDictRow(dat, obj: Dict[str, Any]):
	r = dat.numRows
	dat.appendRow([])
	for key, val in obj.items():
		dat[r, key] = formatValue(val, nonevalue='')

def hextorgb(hexcolor: str):
	if not hexcolor:
		return None
	if hexcolor.startswith('#'):
		hexcolor = hexcolor[1:]
	return _HEXDEC[hexcolor[0:2]], _HEXDEC[hexcolor[2:4]], _HEXDEC[hexcolor[4:6]]

_NUMERALS = '0123456789abcdefABCDEF'
_HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}


# class Color:
# 	def __init__(self, r_or_vals=0, g=0, b=0, a=1):
# 		if isinstance(r_or_vals, (list, tuple)):
# 			vals = r_or_vals
# 			self.r = vals[0] if len(vals) >= 1 else 0
# 			self.g = vals[1] if len(vals) >= 2 else 0
# 			self.b = vals[2] if len(vals) >= 3 else 0
# 			self.a = vals[3] if len(vals) >= 4 else 1
# 		else:
# 			self.r, self.g, self.b, self.a = r_or_vals, g, b, a
#
# 	@classmethod
# 	def ParseHex(cls, hexcolor: str):
# 		return cls()
#
# 	@property
# 	def rgb(self): return self.r, self.g, self.b
#
# 	@property
# 	def rgba(self): return self.r, self.g, self.b, self.a
#
# 	@property
# 	def hsv(self): return rgb_to_hsv(self.r, self.g, self.b)
#
# 	@property
# 	def hsva(self): return self.hsv + (self.a,)
#
# 	@property
# 	def hue(self): return self.hsv[0]
#
# 	@property
# 	def saturation(self): return self.hsv[1]
#
# 	@property
# 	def value(self): return self.hsv[2]
#
# 	def __len__(self): return 4
# 	def __getitem__(self, index): return self.rgba[index]
#
# 	def __repr__(self):
# 		return 'Color({}, {}, {}, {})'.format(*self.rgba)
#
# 	def __hash__(self): return hash(self.rgba)
# 	def __eq__(self, other):
# 		if not other:
# 			return False
# 		if isinstance(other, Color):
# 			return self.rgba == other.rgba
# 		if isinstance(other, (list, tuple)):
# 			return self.rgba == Color(*other)
# 		return False

# variant of defaultdict that passes the key to the factory function
# https://stackoverflow.com/questions/2912231/is-there-a-clever-way-to-pass-the-key-to-defaultdicts-default-factory
class keydefaultdict(defaultdict):
	def __missing__(self, key):
		if self.default_factory is None:
			raise KeyError(key)
		else:
			ret = self[key] = self.default_factory(key)
			return ret

def cartesiantopolar(x, y):
	r = math.hypot(x, y)
	t = math.degrees(math.atan2(y, x))
	return r, t

NULL_PLACEHOLDER = '_'

def parseValue(val, nonevalue=NULL_PLACEHOLDER):
	if val is None or val == nonevalue:
		return None
	if val == '' or isinstance(val, (int, float)):
		return val
	try:
		# noinspection PyTypeChecker
		parsed = float(val)
		if int(parsed) == parsed:
			return int(parsed)
		return parsed
	except ValueError:
		return val

def parseValueList(val):
	if val in (None, ''):
		return []
	if isinstance(val, str):
		return [parseValue(v) for v in val.split(' ')]
	if isinstance(val, int):
		return [val]
	if isinstance(val, (list, tuple)):
		results = []
		for part in val:
			results.append(parseValue(part))
		return results
	raise Exception('Unsupported list value: {!r}'.format(val))


def formatValue(val, nonevalue=NULL_PLACEHOLDER):
	if isinstance(val, str):
		return val
	if val is None:
		return nonevalue
	if isinstance(val, float) and int(val) == val:
		return str(int(val))
	return str(val)


def formatValueList(vals, nonevalue=NULL_PLACEHOLDER):
	if not vals:
		return None
	return ' '.join([formatValue(i, nonevalue=nonevalue) for i in vals])

class ValueRange:
	def __init__(self, valrange):
		self.low, self.high = valrange or (None, None)

	def contains(self, val):
		if self.low is not None and val < self.low:
			return False
		if self.high is not None and val > self.high:
			return False
		return True

	def __repr__(self):
		return '..'.join([
			str(v) if v is not None else '*'
			for v in (self.low, self.high)
		])

class ValueRangeSequence:
	def __init__(self, lows: 'ValueSequence', highs: 'ValueSequence'):
		self.lows = lows
		self.highs = highs

	@classmethod
	def FromSpecs(
			cls,
			lowspec, highspec,
			parse=None,
			cyclic=True,
			lowbackup=None, highbackup=None):
		return cls(
			ValueSequence.FromSpec(lowspec, parse=parse, cyclic=cyclic, backup=lowbackup),
			ValueSequence.FromSpec(highspec, parse=parse, cyclic=cyclic, backup=highbackup),
		)

	def contains(self, val, index: int):
		low = self.lows[index]
		high = self.highs[index]
		if low is not None and val < low:
			return False
		if high is not None and val > high:
			return False
		return True

	def __len__(self):
		return max(len(self.lows), len(self.highs))

	def __str__(self):
		return '{} .. {}'.format(self.lows, self.highs)

	def describeAtIndex(self, index: int):
		return '{} .. {}'.format(
			formatValue(self.lows[index], nonevalue='*'),
			formatValue(self.highs[index], nonevalue='*'))

class ValueSequence:
	def __init__(self, vals, cyclic, backup=None):
		self.vals = list(vals or [])
		self.cyclic = cyclic
		self.backup = backup

	@classmethod
	def FromSpec(cls, spec, parse=None, cyclic=True, backup=None):
		if spec in (None, ''):
			vals = []
		elif isinstance(spec, str):
			vals = spec.split()
		elif isinstance(spec, (list, tuple)):
			vals = spec
		else:
			vals = [spec]
		if parse is None:
			parse = parseValue
		return cls(map(parse, vals), cyclic=cyclic, backup=backup)

	def __len__(self): return len(self.vals)
	def __iter__(self): return iter(self.vals)
	def __bool__(self): return bool(self.vals)

	def __getitem__(self, index):
		if not self.vals:
			return None
		if 0 <= index < len(self.vals):
			return self.vals[index]
		if self.cyclic:
			return self.vals[index % len(self.vals)]
		elif callable(self.backup):
			return self.backup(index)
		else:
			return self.backup

	def permuteWith(self, otherseq: 'ValueSequence', n=None):
		if n is None:
			n = max(len(self), len(otherseq))
		for i in range(n):
			yield self[i], otherseq[i]

	def __str__(self):
		return '({})'.format(' '.join(map(str, self.vals)))

	def __repr__(self):
		return '{}(vals={!r}, cyclic={!r})'.format(
			type(self).__name__, self.vals, self.cyclic)

def longestcommonprefix(strs):
	if not strs:
		return []
	for i, letter_group in enumerate(zip(*strs)):
		# ["flower","flow","flight"]
		# print(i,letter_group,set(letter_group))
		# 0 ('f', 'f', 'f') {'f'}
		if len(set(letter_group)) > 1:
			return strs[0][:i]
	else:
		return min(strs)

class opattrs:
	def __init__(
			self,
			order=None,
			nodepos=None,
			tags=None,
			panelparent=None,
			parvals=None,
			parexprs=None,
			storage=None,
			dropscript=None,
			cloneimmune=None,
			dockto=None,
			showdocked=None,
	):
		self.order = order
		self.nodepos = nodepos
		self.tags = set(tags) if tags else None  # type: Set[str]
		self.panelparent = panelparent
		self.parvals = parvals  # type: Dict[str, Any]
		self.parexprs = parexprs  # type: Dict[str, str]
		self.storage = storage  # type: Dict[str, Any]
		self.dropscript = dropscript  # type: Union[OP, str]
		self.cloneimmune = cloneimmune  # type: Union[bool, str]
		self.dockto = dockto  # type: OP
		self.showdocked = showdocked  # type: bool

	def override(self, other: 'opattrs'):
		if not other:
			return self
		if other.order is not None:
			self.order = other.order
		self.nodepos = other.nodepos or self.nodepos
		if other.cloneimmune is not None:
			self.cloneimmune = other.cloneimmune
		self.dockto = other.dockto or self.dockto
		if other.showdocked is not None:
			self.showdocked = other.showdocked
		if other.tags:
			if self.tags:
				self.tags.update(other.tags)
			else:
				self.tags = set(other.tags)
		if other.storage:
			if self.storage:
				self.storage.update(other.storage)
			else:
				self.storage = dict(other.storage)
		self.panelparent = other.panelparent or self.panelparent
		self.dropscript = other.dropscript or self.dropscript
		self.parvals = mergedicts(self.parvals, other.parvals)
		self.parexprs = mergedicts(self.parexprs, other.parexprs)
		return self

	def applyto(self, o: OP):
		if self.order is not None:
			o.par.alignorder = self.order
		if self.parvals:
			for key, val in self.parvals.items():
				setattr(o.par, key, val)
		if self.parexprs:
			for key, expr in self.parexprs.items():
				getattr(o.par, key).expr = expr
		if self.nodepos:
			o.nodeCenterX = self.nodepos[0]
			o.nodeCenterY = self.nodepos[1]
		if self.tags:
			o.tags.update(self.tags)
		if self.panelparent:
			self.panelparent.outputCOMPConnectors[0].connect(o)
		if self.dropscript:
			o.par.drop = 'legacy'
			o.par.dropscript = self.dropscript
		if self.storage:
			for key, val in self.storage.items():
				if val is None:
					o.unstore(key)
				else:
					o.store(key, val)
		if self.cloneimmune == 'comp':
			o.componentCloneImmune = True
		elif self.cloneimmune is not None:
			o.cloneImmune = self.cloneimmune
		if self.dockto:
			o.dock = self.dockto
		if self.showdocked is not None:
			o.showDocked = self.showdocked
		return o

	@classmethod
	def merged(cls, *attrs, **kwargs):
		result = cls()
		for a in attrs:
			if not a:
				continue
			if isinstance(a, (list, tuple, set)):
				for suba in a:
					if suba:
						result.override(suba)
			else:
				result.override(a)
		if kwargs:
			result.override(cls(**kwargs))
		return result

def updateOP(
		comp,
		attrs: opattrs=None, **kwargs):
	opattrs.merged(attrs, **kwargs).applyto(comp)
	return comp

def _resolveDest(dest):
	deststr = str(dest)
	dest = op(dest)
	if not dest or not dest.isCOMP:
		raise Exception('Invalid destination: {}'.format(deststr))
	return dest

def createFromTemplate(
		template,
		dest, name,
		attrs: opattrs=None, **kwargs):
	dest = _resolveDest(dest)
	comp = dest.copy(template, name=name)
	opattrs.merged(attrs, **kwargs).applyto(comp)
	return comp

def createOP(
		optype, dest, name,
		attrs: opattrs=None, **kwargs):
	dest = _resolveDest(dest)
	comp = dest.create(optype, name)
	opattrs.merged(attrs, **kwargs).applyto(comp)
	return comp

def getOrCreateOP(
		optype, dest, name,
		attrs: opattrs=None, **kwargs):
	comp = dest.op(name)
	if not comp:
		comp = createOP(
			optype,
			dest=dest,
			name=name,
			attrs=attrs,
			**kwargs)
	return comp
