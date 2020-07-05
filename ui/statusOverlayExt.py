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

	def Clearmessages(self, par: 'Par'):
		self.ClearAllMessages()

	def getMessageById(self, messageId: int):
		for record in self.messages:
			if record.id == messageId:
				return record

	def AddMessage(self, message: str):
		return self.addMessage(message, transient=True)

	def AddStaticMessage(self, message: str):
		return self.addMessage(message, transient=False)

	@staticmethod
	def now():
		return absTime.seconds

	def addMessage(self, message: str, transient: bool):
		# self.ownerComp.par.Transientduration.eval()
		if transient:
			record = _Message(
				self.nextId, message, self.now() + self.ownerComp.par.Transientduration)
		else:
			record = _Message(self.nextId, message)
		self.nextId += 1
		self.messages.append(record)
		self.updateUI()
		if transient:
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
