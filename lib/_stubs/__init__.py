# trick pycharm

from typing import List as _List, Union as _Union, Tuple as _Tuple

class _Expando:
	def __init__(self):
		pass

mod = _Expando()
ui = _Expando()
ui.panes = []
ui.panes.current = None
ui.status = ''
PaneType = _Expando()
PaneType.NETWORKEDITOR = None

class project:
	name = ''
	folder = ''
	saveVersion = ''
	saveBuild = ''
	saveTime = ''
	saveOsName = ''
	saveOsVersion = ''
	paths = {}
	cookRate = 0.0
	realTime = True
	isPrivate = False
	isPrivateKey = False


class _Monitor:
	def __init__(self):
		self.index = 0
		self.isPrimary = False
		self.isAffinity = False
		self.width = 0
		self.height = 0
		self.left = 0
		self.right = 0
		self.top = 0
		self.bottom = 0
		self.displayName = ''
		self.description = ''
		self.dpiScale = 0.0
		self.scaledWidth = 0
		self.scaledHeight = 0
		self.scaledLeft = 0
		self.scaledRight = 0
		self.scaledTop = 0
		self.scaledBottom = 0
		self.refreshRate = 0.0


class _Monitors:
	def __init__(self):
		self.primary = _Monitor()
		self.width = 0
		self.height = 0
		self.left = 0
		self.right = 0
		self.top = 0
		self.bottom = 0

	@staticmethod
	def locate(x, y) -> _Monitor:
		pass

	@staticmethod
	def refresh():
		pass

	def __len__(self):
		return 0

monitors = _Monitors()

class sysinfo:
	ram = 0.0

class _Parent:
	def __call__(self, *args, **kwargs):
		return op()

	def __getattr__(self, item):
		pass

class op:
	def __init__(self, arg=None):
		self.id = 0
		self.path = ''
		self.name = ''
		self.par = _Expando()
		self.customTuplets = []
		self.parent = _Parent()
		self.op = op
		self.storage = {}
		self.isCOMP = False
		self.isTOP = False
		self.isCHOP = False
		self.depth = 0
		self.tags = set()
		self.valid = True

	def destroy(self): pass

	def ops(self, *args): return [op()]

	def openParameters(self): pass

	def openViewer(self, unique=False, borders=True): pass

	def closeViewer(self): pass

	def store(self, key, value): pass

	def unstore(self, keys1, *morekeys): pass

	def findChildren(self, maxDepth=1, tags=None) -> '_List[op]': pass

	def addScriptError(self, msg): pass

	def copy(self, o: 'op', name=None) -> 'op': pass

	def create(self, OPtype, name, initialize=True) -> 'op': pass

	TDResources = _Expando()

op.TDResources = _Expando()
op.TDResources.op = op

def ops(*paths):
	return []

def var(name):
	return ''

class _TD_ERROR(Exception):
	pass

class td:
	error = _TD_ERROR
	Monitor = _Monitor
	Monitors = _Monitors

	@staticmethod
	def run(codeorwhatever, *args, delayFrames=0, delayMilliSeconds=0, delayRef=None): pass

	class Attribute:
		def __init__(self):
			self.owner = None  # type: OP
			self.name = ''
			self.size = 0
			self.type = None  # type: type
			self.default = None  # type: _Union[float, int, str, tuple, _Position, _Vector]

del _TD_ERROR

run = td.run

class _Matrix:
	def __init__(self, *values):
		self.vals = []  # type: _List[float]
		self.rows = []  # type: _List[_List[float]]
		self.cols = []  # type: _List[_List[float]]

	def transpose(self): pass

	def invert(self): pass

	def determinant(self) -> float: pass

	def copy(self) -> '_Matrix': pass

	def identity(self): pass

	def translate(self, tx, ty, tz, fromRight=False): pass

	def rotate(self, rx, ry, rz, fromRight=False, pivot=None): pass

	def rotateOnAxis(self, rotationAxis, angle, fromRight=False, pivot=None): pass

	def scale(self, sx, sy, sz, fromRight=False, pivot=None): pass

	def lookat(self, eyePos, target, up): pass

	def decompose(self) -> _Tuple[_Tuple]: pass

class _Position:
	def __init__(self, *vals):
		self.x = self.y = self.z = 0

	def translate(self, x, y, z): pass

	def scale(self, x, y, z): pass

	def copy(self) -> '_Position': pass

	def __getitem__(self, item: int) -> float: pass

	def __setitem__(self, key, value): pass

	def __mul__(self, other: _Union[float, _Matrix]) -> _Union[float, '_Position']: pass

	def __add__(self, other: _Union[float, '_Position', '_Vector']) -> _Union[float, '_Position']: pass

	def __sub__(self, other: _Union[float, '_Position', '_Vector']) -> _Union[float, '_Position']: pass

	def __div__(self, other: float) -> '_Position': pass

	def __abs__(self) -> '_Position': pass

	def __neg__(self) -> '_Position': pass


class _Vector:
	def __init__(self, *vals):
		self.x = self.y = self.z = 0

	def translate(self, x, y, z): pass

	def scale(self, x, y, z): pass

	def __getitem__(self, item: int) -> float: pass

	def __setitem__(self, key, value): pass

	def normalize(self): pass

	def length(self) -> float: pass

	def lengthSquared(self) -> float: pass

	def copy(self) -> '_Vector': pass

	def distance(self, vec: '_Vector') -> float: pass

	def lerp(self, vec: '_Vector', t: float) -> '_Vector': pass

	def slerp(self, vec: '_Vector', t: float) -> '_Vector': pass

	def project(self, vec1: '_Vector', vec2: '_Vector'): pass

	def reflect(self, vec: '_Vector'): pass

class tdu:
	@staticmethod
	def legalName(s):
		return s

	@staticmethod
	def clamp(inputVal, min, max):
		return inputVal

	@staticmethod
	def remap(inputVal, fromMin, fromMax, toMin, toMax):
		return inputVal

	class Dependency:
		def __init__(self, _=None):
			self.val = None

		def modified(self): pass

	Position = _Position
	Vector = _Vector
	Matrix = _Matrix

	@staticmethod
	def split(string, eval=False)-> '_List': pass

	@staticmethod
	def match(pattern, inputList, caseSensitive=True) -> '_List[str]': pass

	@staticmethod
	def collapsePath(path): return path

JustifyType = _Expando()
JustifyType.TOPLEFT, JustifyType.TOPCENTER, JustifyType.TOPRIGHT, JustifyType.CENTERLEFT = 0, 0, 0, 0
JustifyType.CENTER = 0
JustifyType.CENTERRIGHT, JustifyType.BOTTOMLEFT, JustifyType.BOTTOMCENTER, JustifyType.BOTTOMRIGHT = 0, 0, 0, 0

ParMode = _Expando()
ParMode.CONSTANT = ParMode.EXPRESSION = ParMode.EXPORT = 0

ExpandoStub = _Expando

class Par:
	def eval(self):
		return None

OP = op

class DAT(OP):
	def row(self, nameorindex): return []

COMP = OP
CHOP = OP
SOP = OP

baseCOMP = panelCOMP = COMP
evaluateDAT = mergeDAT = nullDAT = parameterexecuteDAT = tableDAT = textDAT = scriptDAT = DAT
parameterCHOP = nullCHOP = selectCHOP = CHOP
scriptSOP = SOP

class app:
	name = ''
	build = ''
	launchTime = ''
	product = ''
	version = ''
	osName = ''
	osVersion = ''
