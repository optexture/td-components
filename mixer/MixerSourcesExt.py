# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class MixerSourcesExt:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

# TODO: use dataclasses once I stop caring about supporting TD 2019.10000 series builds
class Source:
	sourceName: str
	legalName: str
	path: str
	shortName: str = None
	compPath: str = None
	videoPath: str = None
	type: str = None
	deviceName: str = None
	active: bool = None
	streaming: bool = None
	fps: int = None
	url: str = None

	@classmethod
	def fieldNames(cls):
		return [
			'sourceName',
			'legalName',
			'path',
			'shortName',
			'compPath',
			'videoPath',
			'type',
			'deviceName',
			'active',
			'streaming',
			'fps',
			'url',
		]

	def asTuple(self):
		return [
			x if x is not None else ''
			for x in [
				self.sourceName,
				self.legalName,
				self.path,
				self.shortName,
				self.compPath,
				self.videoPath,
				self.type,
				self.deviceName,
				self.active,
				self.streaming,
				self.fps,
				self.url,
			]
		]

