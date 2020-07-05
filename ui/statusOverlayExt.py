from typing import List, Optional
from dataclasses import dataclass

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class StatusOverlay:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: panelCOMP
		self.messages = []  # type: List[_Message]
		self.timer = ownerComp.op('update_timer')  # type: timerCHOP
		self.labelComp = ownerComp.op('label')  # type: panelCOMP
		self.nextId = 0

	def ClearAllMessages(self):
		self.stopTimer()
		self.messages.clear()
		self.updateUI()

	def ClearMessage(self, messageId: int):
		record = self.getMessageById(messageId)
		if not record:
			return
		self.messages.remove(record)
		if not self.messages:
			self.stopTimer()
		self.updateUI()

	def getMessageById(self, messageId: int):
		for record in self.messages:
			if record.id == messageId:
				return record

	def AddStaticMessage(self, message: str):
		return self.AddMessage(message, temporary=False)

	def Clearmessages(self, par: 'Par'):
		self.ClearAllMessages()

	def Addtemporarymessage(self, par: 'Par'):
		self.addMessageFromPar(temporary=True)

	def Addstaticmessage(self, par: 'Par'):
		self.addMessageFromPar(temporary=False)

	def addMessageFromPar(self, temporary: bool):
		message = self.ownerComp.par.Messagetoadd.eval()
		print('OMG ADD MESSAGE FROM PAR: ', repr(message))
		if message:
			self.AddMessage(message, temporary=temporary)

	@staticmethod
	def now():
		return absTime.seconds

	def AddMessage(self, message: str, temporary: bool = True):
		if temporary:
			record = _Message(
				self.nextId, message, self.now() + self.ownerComp.par.Temporaryduration)
		else:
			record = _Message(self.nextId, message)
		self.nextId += 1
		self.messages.append(record)
		self.updateUI()
		if temporary:
			# if not self.timer['timer_active']:
			self.startTimer()
		return record.id

	def startTimer(self):
		self.timer.par.start.pulse()

	def stopTimer(self):
		self.timer.par.initialize.pulse()

	def updateUI(self):
		if not self.messages:
			self.labelComp.par.Widgetlabel = ''
			self.ownerComp.par.display = False
		else:
			self.labelComp.par.Widgetlabel = '\n'.join([
				record.text
				for record in self.messages
			])
			self.ownerComp.par.display = True

	def onUpdateTrigger(self):
		needAnotherUpdate = self.clearExpiredMessages()
		self.updateUI()
		if needAnotherUpdate:
			self.startTimer()

	def clearExpiredMessages(self):
		now = self.now()
		self.messages = [
			record
			for record in self.messages
			if record.endTime is None or record.endTime > now
		]
		changed = False
		needAnotherUpdate = False
		filteredMessages = []
		for record in self.messages:
			if record.endTime is None:
				filteredMessages.append(record)
			elif record.endTime > now:
				needAnotherUpdate = True
				filteredMessages.append(record)
			else:
				changed = True
		if changed:
			self.messages = filteredMessages
		return needAnotherUpdate

@dataclass
class _Message:
	id: int
	text: str
	endTime: Optional[float] = None  # in seconds
