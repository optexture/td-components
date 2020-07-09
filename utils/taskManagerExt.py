from typing import Generic, Callable, List, Optional, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

T = TypeVar('T')

class TaskManager:
	def __init__(self):
		self.tasks = []  # type: List[Callable]
		self.totalTasks = 0
		self.batchFutureTasks = 0

	def updateProgress(self):
		pass

	def getProgressRatio(self):
		if not self.tasks:
			return 1
		remaining = max(0, len(self.tasks) - self.batchFutureTasks)
		total = self.totalTasks
		if not total or not remaining:
			return 1
		return 1 - (remaining / total)

	def getFrameInterval(self):
		return 1

	def getDelayRef(self):
		return None

	def onTaskSucceeded(self, result):
		pass

	def onTaskFailed(self, err):
		pass

	def runNextTask(self):
		if not self.tasks:
			self.ClearTasks()
			return
		task = self.tasks.pop(0)
		result = task()

		def _onSuccess(res):
			self.onTaskSucceeded(res)
			self.updateProgress()
			self.queueNextTask()

		def _onFailure(err):
			self.onTaskFailed(err)
			# self.ClearTasks()
			self.updateProgress()
			self.queueNextTask()

		if isinstance(result, Future):
			result.then(success=_onSuccess, failure=_onFailure)
		else:
			_onSuccess(result)

	def queueNextTask(self):
		if not self.tasks:
			self.ClearTasks()
			return
		td.run(
			'args[0].runNextTask()', self,
			delayFrames=self.getFrameInterval(),
			delayRef=self.getDelayRef())

	def AddTaskBatch(self, tasks: List[Callable], label=None) -> 'Future':
		label = f'TaskBatch({label or ""})'
		tasks = [task for task in tasks if task]
		if not tasks:
			return Future.immediate(label=f'{label or ""} (empty batch)')
		result = Future(label=label)
		self.tasks.extend(tasks)

		# TODO: get rid of this and fix the queue system!
		def _noOp():
			# Log('NO-OP for batch: {}'.format(label))
			pass
		self.tasks.append(_noOp)
		self.batchFutureTasks += 1

		def _finishBatch():
			result.resolve()

		self.tasks.append(_finishBatch)
		self.totalTasks += len(tasks)
		self.batchFutureTasks += 1
		self.queueNextTask()
		return result

	def ClearTasks(self):
		self.tasks.clear()
		self.totalTasks = 0
		self.batchFutureTasks = 0
		self.updateProgress()

class Future(Generic[T]):
	def __init__(self, onListen=None, onInvoke=None, label=None):
		self._successCallback = None  # type: Optional[Callable[[Union[T, 'Future']], None]]
		self._failureCallback = None  # type: Optional[Callable[[Union[T, 'Future']], None]]
		self._resolved = False
		self._canceled = False
		self._result = None  # type: Optional[T]
		self._error = None
		self._onListen = onListen  # type: Callable
		self._onInvoke = onInvoke  # type: Callable
		self.label = label

	def then(
			self,
			success: Callable[[Union[T, 'Future']], None] = None,
			failure: Callable[[Union[object, 'Future']], None] = None):
		if self._successCallback or self._failureCallback:
			raise Exception('Future already has success and/or failure callbacks!')
		if self._onListen:
			self._onListen()
		self._successCallback = success
		self._failureCallback = failure
		if self._resolved:
			self._invoke()
		return self

	def _invoke(self):
		if self._error is not None:
			if self._failureCallback:
				self._failureCallback(self._error)
		else:
			if self._successCallback:
				self._successCallback(self._result if self._result is not None else self)
		if self._onInvoke:
			self._onInvoke()

	def _resolve(self, result: T, error):
		if self._canceled:
			return
		if self._resolved:
			raise Exception('Future has already been resolved')
		self._resolved = True
		self._result = result
		self._error = error
		# if self._error is not None:
		# 	Log('FUTURE FAILED {}'.format(self))
		# else:
		# 	Log('FUTURE SUCCEEDED {}'.format(self))
		if self._successCallback or self._failureCallback:
			self._invoke()

	def resolve(self, result: Optional[T] = None):
		self._resolve(result, None)
		return self

	def fail(self, error):
		self._resolve(None, error or Exception())
		return self

	def cancel(self):
		if self._resolved:
			raise Exception('Future has already been resolved')
		self._canceled = True

	@property
	def isResolved(self):
		return self._resolved

	@property
	def result(self) -> T:
		return self._result

	def __str__(self):
		if self._canceled:
			state = 'canceled'
		elif self._resolved:
			if self._error is not None:
				state = 'failed: {}'.format(self._error)
			elif self._result is None:
				state = 'succeeded'
			else:
				state = 'succeeded: {}'.format(self._result)
		else:
			state = 'pending'
		return '{}({}, {})'.format(self.__class__.__name__, self.label or '<>', state)

	@classmethod
	def immediate(cls, value: T = None, onListen=None, onInvoke=None, label=None) -> 'Future[T]':
		future = cls(onListen=onListen, onInvoke=onInvoke, label=label)
		future.resolve(value)
		return future

	@classmethod
	def immediateError(cls, error, onListen=None, onInvoke=None, label=None):
		future = cls(onListen=onListen, onInvoke=onInvoke, label=label)
		future.fail(error)
		return future

	@classmethod
	def of(cls, obj):
		if isinstance(obj, Future):
			return obj
		return cls.immediate(obj)

	@classmethod
	def all(cls, *futures: 'Future', onListen=None, onInvoke=None) -> 'Future[List]':
		if not futures:
			return cls.immediate([], onListen=onListen, onInvoke=onInvoke)
		merged = cls(onListen=onListen, onInvoke=onInvoke)
		state = {
			'succeeded': 0,
			'failed': 0,
			'results': [None] * len(futures),
			'errors': [None] * len(futures),
		}

		def _checkComplete():
			if (state['succeeded'] + state['failed']) < len(futures):
				return
			if state['failed'] > 0:
				merged.fail((state['errors'], state['results']))
			else:
				merged.resolve(state['results'])

		def _makeCallbacks(index):
			def _resolver(val):
				state['results'][index] = val
				state['succeeded'] += 1
				_checkComplete()

			def _failer(err):
				state['errors'][index] = err
				state['failed'] += 1
				_checkComplete()

			return _resolver, _failer

		for i, f in enumerate(futures):
			cls.of(f).then(*_makeCallbacks(i))
		return merged
