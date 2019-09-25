print('loading logs.py...')

from typing import Callable, Dict, Union, List
from datetime import datetime
import json
import socket
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, NOTSET

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
		return _LogLevels.byname.get(val, _LogLevels.notset)

def LogLevelMenuSource():
	return TDF.parMenu(
		[l.name for l in _LogLevels.levels],
		[l.label for l in _LogLevels.levels])

class Message:
	def __init__(
			self,
			message: str=None,
			level: Union[str, LogLevel]=None,
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


class LoggerBase:
	def __init__(self, ownerComp):
		self._indent = 0
		self.ownerComp = ownerComp

	def _HandleMessage(self, message: Message):
		raise NotImplementedError()

	def _PrepareMessage(self, messageordata: Union[Message, str, dict]):
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
		if message.indent is None:
			message.indent = self._indent
		return message

	def _ShouldHandleMessage(self, message: Message):
		return message and message.level.matchesFilter(self.ownerComp.par.Loglevel.eval())

	def LogMessage(
			self,
			messageordata: Union[Message, str, dict],
			indentafter=False,
			unindentbefore=False,
	):
		if unindentbefore:
			self._indent -= 1

		message = self._PrepareMessage(messageordata)

		try:
			if self._ShouldHandleMessage(message):
				self._HandleMessage(message)
		finally:
			if indentafter:
				self._indent += 1

	@staticmethod
	def GetAppInfo():
		return {
			'build': app.build,
			'launchtime': app.launchTime,
			'product': app.product,
			'version': app.version,
		}

	@staticmethod
	def GetSystemInfo():
		return {
			'hostname': socket.gethostname(),
		}



class Logger:
	def __init__(self, ownerComp, handlers: List[LoggerBase]=None):
		self.ownerComp = ownerComp
		self.op = ownerComp.op
		self.par = ownerComp.par
		self.handlers = list(handlers or [])

	def _GetGlobals(self):
		dat = self.op('global_vals')
		return {
			name.val: val.val
			for name, val in dat.rows()
		}

	@staticmethod
	def _GetAppInfo():
		return {
			'td_app': {
				'build': app.build,
				'launchtime': app.launchTime,
				'product': app.product,
				'version': app.version,
			}
		}

	@staticmethod
	def _GetSystemInfo():
		return {
			'sys': {
				'hostname': socket.gethostname(),
			}
		}

	@staticmethod
	def _GetTimestamp():
		return datetime.now().isoformat()

	def _PrepareMessage(self, messageordata: Union[str, dict]=None, data: dict=None):
		return cleandict(mergedicts(
			self._GetGlobals(),
			self._GetAppInfo(),
			self._GetSystemInfo(),
			{'timestamp': self._GetTimestamp()},
			messageordata if isinstance(messageordata, dict) else {'message': messageordata},
			data))

	def SendMessage(self, messageordata: Union[str, dict]=None, data: dict=None):
		msgobj = self._PrepareMessage(messageordata, data)
		msgjson = json.dumps(msgobj)
		self.op('set_message_json').text = msgjson
		web = self.op('web')
		web.text = ''
		web.par.submitfetch.pulse()

	def LogEvent(self, path, opid, event, indentafter=False, unindentbefore=False):
		raise NotImplementedError()


class PrintLogger(LoggerBase):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)

	def _HandleMessage(self, message: Message):
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
