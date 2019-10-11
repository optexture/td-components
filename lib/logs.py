# t3kt/td-components/logs.py
print('loading logs.py...')

from typing import Any, Callable, Dict, Iterable, Union, List, Optional
from datetime import datetime
import json
import socket
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET
from copy import deepcopy

if False:
	from _stubs import *

TDF = op.TDModules.mod.TDFunctions

class _TimestampType:
	def __init__(self, name, label, fmt: Union[str, Callable[[datetime], str]]):
		self.name = name
		self.label = label
		if fmt is None:
			self.format = None
		elif callable(fmt):
			self.format = fmt
		else:
			def _format(dt: datetime):
				return dt.strftime(fmt)
			self.format = _format

	def get(self):
		return self.format(datetime.now()) if self.format else ''

class _TimestampTypes:
	none = _TimestampType('none', 'None', lambda dt: '')
	basictime = _TimestampType('basictime', 'Basic Time', '%H:%M:%S')
	basicdatetime = _TimestampType('basicdatetime', 'Basic Datetime', '%Y.%m.%d %H:%M:%S')
	precisetime = _TimestampType('precisetime', 'Precise Time', '%H:%M:%S.%f')
	precisedatetime = _TimestampType('precisedatetime', 'Precise Datetime', '%Y.%m.%d %H:%M:%S.%f')
	filedate = _TimestampType('filedate', 'File Date', '%Y-%m-%d')
	iso = _TimestampType('iso', 'ISO', lambda dt: dt.isoformat())

	default = basicdatetime

	alltypes = [
		none,
		basictime,
		basicdatetime,
		precisetime,
		precisedatetime,
		filedate,
		iso,
	]
	byname = {t.name: t for t in alltypes}

	@staticmethod
	def getType(name):
		return _TimestampTypes.byname.get(name)

def TimestampTypeMenuSource():
	return TDF.parMenu(
		[t.name for t in _TimestampTypes.alltypes],
		[t.label for t in _TimestampTypes.alltypes])

class LogLevel:
	def __init__(self, name, label, value):
		self.name = name
		self.label = label
		self.value = value

	@staticmethod
	def _getValueOf(level: Union[str, int, 'LogLevel']):
		if hasattr(level, 'value'):
			return level.value
		if isinstance(level, (int, float)):
			return level
		if isinstance(level, str):
			return _LogLevels.getLevel(level).value
		return 0

	def matchesFilter(self, filterlevel: Union[str, int, 'LogLevel']):
		filterlevel = LogLevel._getValueOf(filterlevel)
		if not filterlevel or not self.value:
			return True
		return self.value >= filterlevel

	def __bool__(self):
		return bool(self.value)

	def __repr__(self):
		return '{}({}, {}, {})'.format(type(self), self.name, self.label, self.value)

	def __str__(self):
		return self.name

class _LogLevels:
	notset = LogLevel('notset', 'Not Set', NOTSET)
	debug = LogLevel('debug', 'Debug', DEBUG)
	info = LogLevel('info', 'Info', INFO)
	warning = LogLevel('warning', 'Warning', WARNING)
	error = LogLevel('error', 'Error', ERROR)
	critical = LogLevel('critical', 'Critical', CRITICAL)

	levels = [
		notset,
		debug,
		info,
		warning,
		error,
		critical,
	]

	byname = {l.name: l for l in levels}

	@staticmethod
	def getLevel(val):
		if isinstance(val, LogLevel):
			return val
		if not val:
			return _LogLevels.notset
		if hasattr(val, 'name'):
			val = val.name
		return _LogLevels.byname.get(str(val), _LogLevels.notset)

def LogLevelMenuSource():
	return TDF.parMenu(
		[l.name for l in _LogLevels.levels],
		[l.label for l in _LogLevels.levels])

_LogLevelOrStrT = Union[str, LogLevel]

class Message:
	def __init__(
			self,
			message: str=None,
			level: _LogLevelOrStrT=None,
			timestamp: str=None,
			oppath: str=None,
			opid: str=None,
			subcomp: str=None,
			indent: int=None,
			**data):
		self.message = message
		self.level = _LogLevels.getLevel(level)
		self.timestamp = timestamp
		self.oppath = oppath
		self.opid = opid
		self.subcomp = subcomp
		self.indent = indent or NOTSET
		self.data = data

	def toDict(self):
		return cleandict(mergedicts(
			{
				'message': self.message,
				'level': self.level.value,
				'levelname': self.level.name,
				'timestamp': self.timestamp,
				'oppath': self.oppath,
				'opid': self.opid,
				'subcomp': self.subcomp,
				'indent': self.indent,
			}, self.data))

	def toText(self, useindent=True, timestamptype: _TimestampType=None, includelevel=False):
		if not self.message:
			return ''
		indentstr = ('\t' * self.indent) if useindent and self.indent else ''
		if not self.oppath and not self.opid:
			prefix = ''
		elif self.opid and self.oppath:
			prefix = '{}[{}]'.format(self.opid, self.oppath)
		else:
			prefix = self.opid or self.oppath or ''
		if self.subcomp:
			prefix += ' ' + self.subcomp
		if timestamptype and timestamptype != _TimestampTypes.none:
			timestamp = self.timestamp or timestamptype.get()
			if timestamp:
				prefix = '[{}] {}'.format(timestamp, prefix)
		if includelevel and self.level.value:
			suffix = ' ({})'.format(self.level.name)
		else:
			suffix = ''
		if prefix:
			prefix += ' '
		return prefix + indentstr + str(self.message) + suffix

_MessageOrDataT = Union[Message, str, dict]

class LoggableBase:

	@staticmethod
	def _PrepareLogMessage(messageordata: _MessageOrDataT, level: _LogLevelOrStrT=None):
		if not messageordata:
			return None
		elif isinstance(messageordata, Message):
			message = messageordata
		elif isinstance(messageordata, str):
			message = Message(messageordata)
		elif isinstance(messageordata, dict):
			message = Message(**messageordata)
		else:
			message = Message(str(messageordata))
		if level is not None and not message.level:
			message.level = _LogLevels.getLevel(level)
		return message

	def Log(
			self,
			messageordata: _MessageOrDataT,
			level: _LogLevelOrStrT=None,
			indentafter=False,
			unindentbefore=False,
	):
		raise NotImplementedError()

	def LogBegin(self, message, level=None):
		self.Log(message, indentafter=True, level=level)

	def LogEnd(self, message=None, level=None):
		self.Log(message, unindentbefore=True, level=level)

class LoggerBase(LoggableBase):
	def __init__(self, ownerComp):
		self._indent = 0
		self.ownerComp = ownerComp

	def HandleMessage(self, message: Message):
		raise NotImplementedError()

	def _PrepareMessage(
			self,
			messageordata: _MessageOrDataT,
			level: _LogLevelOrStrT=None,
	):
		message = super()._PrepareLogMessage(messageordata, level=level)
		if message and message.indent is None:
			message.indent = self._indent
		return message

	def _ShouldHandleMessage(self, message: Message):
		return message and message.level.matchesFilter(self.ownerComp.par.Loglevel.eval())

	def SetIndent(self, indent: int):
		self._indent = indent

	def Log(
			self,
			messageordata: _MessageOrDataT,
			level: _LogLevelOrStrT=None,
			indentafter=False,
			unindentbefore=False,
	):
		if unindentbefore:
			self._indent -= 1

		message = self._PrepareMessage(messageordata, level=level)

		try:
			if self._ShouldHandleMessage(message):
				self.HandleMessage(message)
		finally:
			if indentafter:
				self._indent += 1

class _InfoDetailLevels:
	none = 0
	basic = 1
	detailed = 2
	verbose = 3

def _GetAppInfo(detaillevel=_InfoDetailLevels.basic):
	if detaillevel <= _InfoDetailLevels.none:
		return None
	return {
		'build': app.build,
		'launchtime': app.launchTime,
		'product': app.product,
		'version': app.version,
	}

def _GetSystemInfo(detaillevel=_InfoDetailLevels.basic):
	if detaillevel <= _InfoDetailLevels.none:
		return None
	info = {
		'hostname': socket.gethostname(),
		'osName': app.osName,
		'osVersion': app.osVersion,
	}
	if detaillevel >= _InfoDetailLevels.detailed:
		info.update({
			'ramGB': round(sysinfo.ram / 1024 / 1024 / 1024, 4),
		})
	return info

def _GetProjectInfo(detaillevel=_InfoDetailLevels.basic):
	if detaillevel <= _InfoDetailLevels.none:
		return None
	info = {
		'name': project.name,
		'folder': project.folder,
		'saveVersion': project.saveVersion,
		'saveBuild': project.saveBuild,
		'saveTime': project.saveTime,
	}
	if detaillevel >= _InfoDetailLevels.detailed:
		info.update({
			'saveOsName': project.saveOsName,
			'saveOsVersion': project.saveOsVersion,
		})
	return info

def _GetMonitorsInfo(detaillevel=_InfoDetailLevels.basic):
	if detaillevel <= _InfoDetailLevels.none:
		return None
	info = {
		'primary': monitors.primary.index if monitors.primary is not None else -1,
		'width': monitors.width,
		'height': monitors.height,
		'count': len(monitors),
	}
	if detaillevel >= _InfoDetailLevels.detailed:
		info.update({
			'left': monitors.left,
			'right': monitors.right,
			'top': monitors.top,
			'bottom': monitors.bottom,
			'monitors': [_GetMonitorInfo(m, detaillevel) for m in monitors]
		})
	return info

def _GetMonitorInfo(m: 'td.Monitor', detaillevel=_InfoDetailLevels.basic):
	if detaillevel < _InfoDetailLevels.detailed:
		return None
	info = {
		'index': m.index,
		'isPrimary': m.isPrimary,
		'width': m.width,
		'height': m.height,
		'left': m.left,
		'right': m.right,
		'top': m.top,
		'bottom': m.bottom,
		'displayName': m.displayName,
		'refreshRate': m.refreshRate,
	}
	if detaillevel > _InfoDetailLevels.verbose:
		info.update({
			'isAffinity': m.isAffinity,
			'description': m.description,
			'dpiScale': m.dpiScale,
			'scaledWidth': m.scaledWidth,
			'scaledHeight': m.scaledHeight,
			'scaledLeft': m.scaledLeft,
			'scaledRight': m.scaledRight,
			'scaledTop': m.scaledTop,
			'scaledBottom': m.scaledBottom,
		})
	return info

def _BuildInfo(
		applevel=_InfoDetailLevels.basic,
		syslevel=_InfoDetailLevels.basic,
		projectlevel=_InfoDetailLevels.basic,
		monitorslevel=_InfoDetailLevels.none):
	return cleandict({
		'LOL': 'foooo',
		'app': _GetAppInfo(applevel),
		'sys': _GetSystemInfo(syslevel),
		'project': _GetProjectInfo(projectlevel),
		'monitors': _GetMonitorsInfo(monitorslevel),
	})


class PrintLogger(LoggerBase):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)

	def HandleMessage(self, message: Message):
		text = message.toText(
			useindent=True,
			timestamptype=_TimestampTypes.getType(str(self.ownerComp.par.Timestamptype)),
			includelevel=self.ownerComp.par.Includelevel)
		if text:
			self._PrintText(text)
			msglog = self.ownerComp.op('message_log')
			if msglog.par.maxlines:
				msglog.appendRow([text])

	def _PrintText(self, text: str):
		print(text)

class ConsoleLogger(PrintLogger):
	pass

class FileLogger(PrintLogger):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self._file = None
		self._hasnofile = False

	def ResetFile(self):
		if self._file:
			self._file.close()
		self._file = None
		self._hasnofile = False

	def _InitializeFile(self):
		if self._file:
			self._file.close()
			self._file = None
		self._hasnofile = True
		mode = self.ownerComp.par.Filemode.eval()
		append = self.ownerComp.par.Appendtofile.eval()
		if mode == 'simple':
			filename = self.ownerComp.par.Logfile.eval()
			if filename:
				self._file = open(filename, 'a' if append else 'w')
				self._hasnofile = False

	def _PrintText(self, text: str):
		if self._hasnofile:
			return
		if not self._file:
			self._InitializeFile()
		print(text, file=self._file, flush=True)

class MultiLogger(LoggerBase):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self.loggers = []  # type: List[LoggerBase]
		self.AttachLoggers()

	def AttachLoggers(self):
		self.loggers = [self.ownerComp.op('./console_logger'), self.ownerComp.op('./file_logger')]
		self.loggers += self.ownerComp.par.Loggers.evalOPs() or []

	def HandleMessage(self, message: Message):
		for logger in self.loggers:
			try:
				logger.HandleMessage(deepcopy(message))
			except Exception as err:
				errmessage = 'ERROR in logger [{}]: {}'.format(logger, err)
				print(errmessage)
				self.ownerComp.addScriptError(errmessage)

class LogglyLogger(LoggerBase):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self.webdat = self.ownerComp.op('web')
		self.msgjsondat = self.ownerComp.op('set_message_json')

	def _PrepareMessage(
			self,
			messageordata: _MessageOrDataT,
			level: _LogLevelOrStrT=None,
	):
		message = super()._PrepareMessage(messageordata, level=level)
		if not message:
			return None
		info = self._BuildInfo()
		if info:
			message.data.update(info)
		return message

	def _BuildInfo(self):
		return _BuildInfo(
			applevel=self.ownerComp.par.Appinfolevel.menuIndex,
			syslevel=self.ownerComp.par.Sysinfolevel.menuIndex,
			projectlevel=self.ownerComp.par.Projectinfolevel.menuIndex,
			monitorslevel=self.ownerComp.par.Monitorinfolevel.menuIndex,
		)

	def HandleMessage(self, message: Message):
		if not self.ownerComp.par.Endpointurl:
			self.ownerComp.addWarning('No endpoint URL set for logger')
			return
		msgobj = message.toDict()
		if not msgobj:
			return
		msgjson = json.dumps(msgobj)
		self.msgjsondat.text = msgjson
		self.webdat.text = ''
		self.webdat.par.submitfetch.pulse()

	def HandleResponse(self, text):
		success = self._IsSuccessResponse(text)
		if success is None:
			return
		if success:
			self.ownerComp.clearScriptErrors(recurse=False, error='LogglyLogger*')
		else:
			self.ownerComp.addScriptError('LogglyLogger: ' + text)

	@staticmethod
	def _IsSuccessResponse(text):
		if not text:
			return None
		if text == '{"response" : "ok"}':
			return True
		if text.startswith('{'):
			obj = json.loads(text)
			if obj.get('response') == 'ok':
				return True
		return False


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

class LoggableExtension(LoggableBase):
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.logId = self._GetLogId()
		self.getlogger = lambda: None  # type: Callable[[], Optional[LoggerBase]]
		if hasattr(ownerComp.par, 'Logger'):
			self.getlogger = lambda: self.ownerComp.par.Logger.eval()
		elif hasattr(op, 'Logger'):
			self.getlogger = lambda: op.Logger

	def _GetLogId(self) -> Optional[str]:
		if not self.ownerComp.valid or not hasattr(self.ownerComp.par, 'opshortcut'):
			return None
		return self.ownerComp.par.opshortcut.eval()

	def _PrepareLogMessage(
			self,
			messageordata: _MessageOrDataT,
			level: _LogLevelOrStrT=None,
	):
		message = super()._PrepareLogMessage(messageordata, level=level)
		if not message:
			return None
		message.opid = message.opid or self.logId
		message.oppath = message.oppath or self.ownerComp.path
		return message

	def Log(
			self,
			messageordata: _MessageOrDataT,
			level: _LogLevelOrStrT=None,
			indentafter=False,
			unindentbefore=False,
	):
		message = self._PrepareLogMessage(messageordata, level=level)
		logger = self.getlogger()  # type: LoggerBase
		if logger:
			logger.Log(message, indentafter=indentafter, unindentbefore=unindentbefore)

def _FormatArgLimited(arg, limit):
	s = repr(arg)
	if len(s) > limit:
		return s[0:(limit-3)] + '...'
	return s

class _LoggedMethodDecorator:
	def __init__(
			self,
			level: _LogLevelOrStrT=_LogLevels.info,
			omitargs: Union[Iterable[str], bool]=None,
			limitarglength: Optional[int]=100,
			verboseend=False,
		):
		self.level = _LogLevels.getLevel(level)
		self.verboseend = verboseend
		self.formatargs = None  # type: Callable[[Iterable, dict], str]
		if omitargs is True:
			self.formatargs = lambda args, kwargs: ''
		else:
			argstoskip = omitargs or []
			if limitarglength:
				def formatsinglearg(arg): _FormatArgLimited(arg, limitarglength)
			else:
				formatsinglearg = repr

			def _formatargs(args, kwargs):
				text = ''
				if args:
					text = ', '.join(formatsinglearg(arg) for arg in args)
				if kwargs:
					if text:
						text += ', '
					text += ', '.join(
						name + ': ' + formatsinglearg(val)
						for name, val
						in kwargs.items()
						if name not in argstoskip
					)
				return text
			self.formatargs = _formatargs

	def __call__(self, func):
		def _wrapped(selfobj: LoggableBase, *args, **kwargs):
			messagetext = '{}({})'.format(func.__name__, self.formatargs(args, kwargs))
			selfobj.LogBegin(messagetext, level=self.level)
			try:
				return func(selfobj, *args, **kwargs)
			finally:
				selfobj.LogEnd(messagetext if self.verboseend else None, level=self.level)
		return _wrapped

def customloggedmethod(
		level: _LogLevelOrStrT=_LogLevels.info,
		omitargs: Union[Iterable[str], bool]=None,
		limitarglength: Optional[int]=100,
		verboseend=False,
):
	return _LoggedMethodDecorator(
		level=level,
		omitargs=omitargs,
		limitarglength=limitarglength,
		verboseend=verboseend)

def loggedmethod(func):
	return _LoggedMethodDecorator()(func)

def simpleloggedmethod(func):
	return _LoggedMethodDecorator(omitargs=True)(func)
