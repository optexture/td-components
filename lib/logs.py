print('loading logs.py...')

from typing import Callable, Dict, Union, List
from datetime import datetime
import json
import socket
from logging import CRITICAL, FATAL, ERROR, WARN, WARNING, INFO, DEBUG, NOTSET
from logging import getLevelName

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

def TimestampTypeMenuSource():
	return TDF.parMenu(
		[t.name for t in _TimestampTypes.alltypes],
		[t.label for t in _TimestampTypes.alltypes])

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
	byname = {
		t.name: t
		for t in alltypes
	}

	@staticmethod
	def getType(name):
		return _TimestampTypes.byname.get(name)


class Message:
	def __init__(
			self,
			message: str=None,
			level=INFO,
			timestamp: str=None,
			oppath: str=None,
			opid: str=None,
			subcomp: str=None,
			indent: int=None,
			**data):
		self.message = message
		self.level = level
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
				'level': self.level,
				'levelname': getLevelName(self.level),
				'timestamp': self.timestamp,
				'oppath': self.oppath,
				'opid': self.opid,
				'subcomp': self.subcomp,
				'indent': self.indent,
			}, self.data))

	def toText(self, useindent=True, timestamptype: _TimestampType=None):
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
		if prefix:
			prefix += ' '
		return prefix + indentstr + str(self.message)


class LogHandlerBase:
	def __init__(self):
		self._indent = 0

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

	def HandleMessage(
			self,
			messageordata: Union[Message, str, dict],
			indentafter=False,
			unindentbefore=False,
	):
		if unindentbefore:
			self._indent -= 1

		message = self._PrepareMessage(messageordata)

		try:
			if message:
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
	def __init__(self, ownerComp, handlers: List[LogHandlerBase]=None):
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


class PrintLogHandler(LogHandlerBase):
	def __init__(self, ownerComp):
		super().__init__()
		self.ownerComp = ownerComp

	def _GetFile(self):
		return None

	def _HandleMessage(self, message: Message):
		text = message.toText(useindent=True, timestamptype=_TimestampTypes.getType(str(self.ownerComp.par.Timestamptype)))
		if text:
			print(text, file=self._GetFile())

class ConsoleLogHandler(PrintLogHandler):
	pass


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
