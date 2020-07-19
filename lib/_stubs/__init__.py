# trick pycharm

from abc import ABC as _ABC
# noinspection PyShadowingBuiltins
import typing as _T
import enum as _E

# noinspection PyUnreachableCode
if False:
	import numpy

class _Expando:
	def __init__(self):
		pass

mod = _Expando()
ui: 'UI'
PaneType = _Expando()
PaneType.NETWORKEDITOR = None

class PaneType(_E.Enum):
	NETWORKEDITOR = 0
	PANEL = 0
	GEOMETRYVIEWER = 0
	TOPVIEWER = 0
	CHOPVIEWER = 0
	ANIMATIONEDITOR = 0
	PARAMETERS = 0
	TEXTPORT = 0

ext = _Expando()  # type: _T.Any

class UI:
	clipboard: str
	colors: _T.Any #td.Colors
	dpiBiCubicFilter: bool
	masterVolume: float
	options: _T.Any #td.Options
	panes: 'Panes'
	performMode: bool
	preferences: _T.Any #td.Preferences
	redrawMainWindow: bool
	rolloverOp: 'OP'
	rolloverPar: 'Par'
	lastChopChannelSelected: 'Par'
	showPaletteBrowser: bool
	status: str
	undo: 'Undo'

	def copyOPs(self, listOfOPs): pass
	# noinspection PyShadowingNames
	def pasteOPs(self, COMP, x=None, y=None): pass
	# noinspection PyDefaultArgument
	def messageBox(self, title, message, buttons=['Ok'])-> int: pass
	def refresh(self): pass
	def chooseFile(self, load=True, start=None, fileTypes=None, title=None, asExpression=False) -> _T.Optional[str]: pass
	def chooseFolder(self, title='Select Folder', start=None, asExpression=False) -> _T.Optional[str]: pass
	def viewFile(self, url_or_path): pass
	def openAbletonControl(self): pass
	def openBeat(self): pass
	def openBookmarks(self): pass
	def openCOMPEditor(self, path): pass
	def openConsole(self): pass
	def openDialogHelp(self, title): pass
	def openErrors(self): pass
	def openExplorer(self): pass
	def openExportMovie(self, path=""): pass
	def openHelp(self): pass
	def openImportFile(self): pass
	def openKeyManager(self): pass
	def openMIDIDeviceMapper(self): pass
	def openNewProject(self): pass
	def openOperatorSnippets(self, family=None, type=None, example=None): pass
	def openPaletteBrowser(self): pass
	def openPerformanceMonitor(self): pass
	def openPreferences(self): pass
	def openSearch(self): pass
	def openTextport(self): pass
	def openVersion(self): pass
	def openWindowPlacement(self): pass

	status: str

class Panes:
	def __getitem__(self, key) -> 'Pane': pass
	def __iter__(self) -> _T.Iterator['Pane']: pass
	def __len__(self) -> int: pass
	def __next__(self) -> 'Pane': pass
	# noinspection PyShadowingBuiltins
	def createFloating(
			self,
			type=PaneType.NETWORKEDITOR,
			name=None,
			maxWidth=1920, maxHeight=1080,
			monitorSpanWidth=0.9, monitorSpanHeight=0.9,
	) -> 'Pane': pass

	current: 'Pane'

Coords = _T.NamedTuple('Coords', [('x', int), ('y', int), ('u', float), ('v', float)])

class Pane:
	def changeType(self, paneType: 'PaneType') -> 'Pane': pass
	def close(self): pass
	def floatingCopy(self) -> 'Pane': pass
	def splitBottom(self) -> 'Pane': pass
	def splitLeft(self) -> 'Pane': pass
	def splitRight(self) -> 'Pane': pass
	def splitTop(self) -> 'Pane': pass
	def tearAway(self) -> bool: pass

	bottomLeft: 'Coords'
	id: int
	link: int
	maximize: bool
	name: str
	owner: 'COMP'
	ratio: float
	topRight: 'Coords'
	type: 'PaneType'

class NetworkEditor(Pane):
	showBackdropCHOPs: bool
	showBackdropGeometry: bool
	showBackdropTOPs: bool
	showColorPalette: bool
	showDataLinks: bool
	showList: bool
	showNetworkOverview: bool
	showParameters: bool
	straightLinks: bool
	x: float
	y: float
	zoom: float

	def fitWidth(self, width) -> None: pass

	def fitHeight(self, height) -> None: pass

	def home(self, zoom=True, op=None) -> None: pass

	def homeSelected(self, zoom=True) -> None: pass

	def placeOPs(self, listOfOPs, inputIndex=None, outputIndex=None, delOP=None, undoName='Operators') -> None: pass

class Undo:
	globalState: bool
	redoStack: list
	state: bool
	undoStack: list

	def startBlock(self, name, enable=True): pass
	def clear(self): pass
	def addCallback(self, callback: _T.Callable[[bool, _T.Any], None], info=None): pass
	def redo(self): pass
	def undo(self): pass
	def endBlock(self): pass

class Project:
	name: str
	folder: str
	saveVersion: str
	saveBuild: str
	saveTime: str
	saveOsName: str
	saveOsVersion: str
	paths: _T.Dict[str, str]
	cookRate: float
	realTime: bool
	isPrivate: bool
	isPrivateKey: bool

project: Project

class Monitor:
	index: int
	isPrimary = False
	isAffinity = False
	width: int
	height: int
	left: int
	right: int
	top: int
	bottom: int
	displayName: str
	description: str
	dpiScale: float
	scaledWidth: int
	scaledHeight: int
	scaledLeft: int
	scaledRight: int
	scaledTop: int
	scaledBottom: int
	refreshRate: float

class Monitors:
	primary: Monitor
	width: 0
	height: 0
	left: 0
	right: 0
	top: 0
	bottom: 0

	@staticmethod
	def locate(x, y) -> Monitor:
		pass

	@staticmethod
	def refresh():
		pass

	def __len__(self):
		return 0

monitors:  Monitors

class SysInfo:
	ram: float

sysinfo: SysInfo

class _Parent:
	def __call__(self, *args, **kwargs) -> '_AnyOpT': pass
	def __getattr__(self, item) -> '_AnyOpT': pass

parent: _Parent

class Channel:
	valid: bool
	index: int
	name: str
	owner: '_AnyOpT'
	exports: list
	vals: _T.List[float]

	def __getitem__(self, index: int) -> float: pass
	def __setitem__(self, index: int, value: _T.Union[int, float]): pass
	def eval(self, index: _T.Optional[int] = None) -> float: pass
	def evalFrame(self, frame) -> float: pass
	def evalSeconds(self, secs) -> float: pass
	def numpyArray(self) -> numpy.array: pass
	def destroy(self) -> None: pass
	def average(self) -> float: pass
	def min(self) -> float: pass
	def max(self) -> float: pass
	def __int__(self) -> int: pass
	def __float__(self) -> float: pass

_ValueT = _T.Union[float, int, str]

class Par:
	valid: bool
	val: _ValueT
	expr: str
	exportOP: _T.Optional['OP']
	exportSource: _T.Optional[_T.Union['Cell', 'Channel']]
	bindExpr: str
	bindMaster: _T.Optional['OP']
	bindReferences: list
	index: int
	vecIndex: int
	name: str
	label: str

	startSection: bool
	readOnly: bool
	tuplet: '_ParTupletT'
	tupletName: str
	min: _ValueT
	max: _ValueT
	clampMin: bool
	clampMax: bool
	default: _ValueT
	defaultExpr: str
	normMin: float
	normMax: float
	normVal: float
	enable: bool
	order: int
	page: 'Page'
	password: bool

	mode: 'ParMode'
	prevMode: 'ParMode'
	menuNames: _T.List[str]
	menuLabels: _T.List[str]
	menuIndex: int
	menuSource: str
	owner: 'OP'

	isDefault: bool
	isCustom: bool
	isPulse: bool
	isMomentary: bool
	isMenu: bool
	isNumber: bool
	isFloat: bool
	isInt: bool
	isOP: bool
	isPython: bool
	isString: bool
	isToggle: bool
	style: str

	def copy(self, par: 'Par') -> None: pass
	def eval(self) -> _T.Union[_ValueT, '_AnyOpT']: pass
	def evalNorm(self) -> _ValueT: pass
	def evalExpression(self) -> _ValueT: pass
	def evalExport(self) -> _ValueT: pass
	def evalOPs(self) -> list: pass
	def pulse(self, value, frames=0, seconds=0) -> None: pass
	def destroy(self) -> None: pass

	def __int__(self) -> int: pass
	def __float__(self) -> float: pass
	def __str__(self) -> str: pass

_ParTupletT = _T.Union[
	_T.Tuple['Par'], _T.Tuple['Par', 'Par'], _T.Tuple['Par', 'Par', 'Par'], _T.Tuple['Par', 'Par', 'Par', 'Par']]

class Page:
	name: str
	owner: 'OP'
	parTuplets: _T.List[_ParTupletT]
	pars: _T.List['Par']
	index: int

	def _appendSized(self, name, label=None, size=1, order=None, replace=True) -> _ParTupletT: pass
	def _appendBasic(self, name, label=None, order=None, replace=True) -> _ParTupletT: pass

	appendInt = appendFloat = _appendSized
	appendOP = appendCHOP = appendDAT = appendMAT = appendTOP = appendSOP = _appendBasic
	appendCOMP = appendOBJ = appendPanelCOMP = _appendBasic
	appendMenu = appendStr = appendStrMenu = _appendBasic
	appendWH = appendRGBA = appendRGB = appendXY = appendXYZ = appendUV = appendUVW = _appendBasic
	appendToggle = appendPython = appendFile = appendFolder = _appendBasic
	appendPulse = appendMomentary = _appendBasic

	def appendPar(self, name: str, par: 'Par' = None, label=None, order=None, replace=True) -> _ParTupletT: pass

	def sort(self, *parameters: str): pass
	def destroy(self): pass

class OP:
	valid: bool
	id: int
	name: str
	path: str
	digits: int
	base: str
	passive: bool
	curPar: 'Par'
	time: 'timeCOMP'
	ext: _T.Any
	mod: _T.Any
	par: _T.Any
	customPars: _T.List['Par']
	customPages: _T.List['Page']
	customTuplets: _T.List[_ParTupletT]
	replicator: _T.Optional['OP']
	storage: _T.Dict[str, _T.Any]
	tags: _T.Set[str]
	children: _T.List['_AnyOpT']
	numChildren: int
	numChildrenRecursive: int
	parent: '_Parent'
	iop: _T.Any
	ipar: _T.Any

	activeViewer: bool
	allowCooking: bool
	bypass: bool
	cloneImmune: bool
	current: bool
	display: bool
	expose: bool
	lock: bool
	selected: bool
	python: bool
	render: bool
	showCustomOnly: bool
	showDocked: bool
	viewer: bool

	color: _T.Tuple[float, float, float]
	comment: str
	nodeHeight: int
	nodeWidth: int
	nodeX: int
	nodeY: int
	nodeCenterX: int
	nodeCenterY: int
	dock: 'OP'
	docked: _T.List['_AnyOpT']

	inputs: _T.List['_AnyOpT']
	outputs: _T.List['_AnyOpT']
	inputConnectors: _T.List['Connector']
	outputConnectors: _T.List['Connector']

	cookFrame: float
	cookTime: float
	cpuCookTime: float
	cookAbsFrame: float
	cookStartTime: float
	cookEndTime: float
	cookedThisFrame: bool
	cookedPreviousFrame: bool
	childrenCookTime: float
	childrenCPUCookTime: float
	childrenCookAbsFrame: float
	childrenCPUCookAbsFrame: float
	gpuCookTime: float
	childrenGPUCookTime: float
	childrenGPUCookAbsFrame: float
	totalCooks: int
	cpuMemory: int
	gpuMemory: int

	type: str
	subType: str
	OPType: str
	label: str
	icon: str
	family: str
	isFilter: bool
	minInputs: int
	maxInputs: int
	isMultiInputs: bool
	visibleLevel: int
	isBase: bool
	isCHOP: bool
	isCOMP: bool
	isDAT: bool
	isMAT: bool
	isObject: bool
	isPanel: bool
	isSOP: bool
	isTOP: bool
	licenseType: str

	def __init__(self): pass

	def destroy(self): pass

	def op(self, path) -> '_AnyOpT': pass
	def ops(self, *args) -> _T.List['_AnyOpT']: pass
	def shortcutPath(self, o: '_AnyOpT', toParName=None) -> str: pass
	def relativePath(self, o: '_AnyOpT') -> str: pass
	def openMenu(self, x=None, y=None): pass
	def var(self, name, search=True) -> str: pass
	def evalExpression(self, expr) -> _T.Any: pass
	def dependenciesTo(self, o: '_AnyOpT') -> _T.List['_AnyOpT']: pass
	def changeType(self, optype: _T.Type) -> '_AnyOpT': pass
	def copyParameters(self, o: '_AnyOpT', custom=True, builtin=True): pass
	def cook(self, force=False, recurse=False): pass
	def pars(self, *pattern: str) -> _T.List['Par']: pass

	def openParameters(self): pass
	def openViewer(self, unique=False, borders=True): pass
	def closeViewer(self): pass

	def store(self, key, value): pass
	def unstore(self, keys1, *morekeys): pass
	def storeStartupValue(self, key, value): pass
	def unstoreStartupValue(self, *keys): pass
	def fetch(self, key, default=None, search=True, storeDefault=False): pass
	def fetchOwner(self, key) -> '_AnyOpT': pass

	def addScriptErrors(self, msg): pass
	def addError(self, msg): pass
	def addWarning(self, msg): pass
	def errors(self, recurse=False) -> str: pass
	def warnings(self, recurse=False) -> str: pass
	def scriptErrors(self, recurse=False) -> str: pass
	def clearScriptErrors(self, recurse=False, error='*'): pass

	TDResources = _Expando()

def op(path) -> '_AnyOpT': pass

op.TDResources = _Expando()
op.TDResources.op = op

iop = _Expando()  # type: _T.Any
ipar = _Expando()  # type: _T.Any

def ops(*paths) -> _T.List['_AnyOpT']: pass

def var(name) -> str: pass

class td:
	Monitor = Monitor
	Monitors = Monitors
	Attribute = Attribute
	me: 'OP'
	absTime: _T.Any #absTime
	app: 'App'
	ext: _T.Any
	families: dict
	licenses: _T.Any #licenses
	mod: mod
	monitors: 'Monitors'
	op: 'OP'
	parent: '_Parent'
	iop: 'OP'
	ipar: 'OP'
	project: 'Project'
	root: 'OP'
	runs: _T.Any #runs
	sysinfo: 'SysInfo'
	ui: 'UI'

	@classmethod
	def passive(cls, OP) -> 'OP': pass
	@classmethod
	def run(
			cls, script, *args, endFrame=False, fromOP: 'OP' = None, asParameter=False, group=None, delayFrames=0,
			delayMilliSeconds=0, delayRef: 'OP' = None) -> _T.Any: #Run
		pass
	@classmethod
	def fetchStamp(cls, key, default) -> _T.Union[_ValueT, str]: pass
	@classmethod
	def var(cls, varName) -> str: pass
	@classmethod
	def varExists(cls, varName) -> bool: pass
	@classmethod
	def varOwner(cls, varName) -> _T.Optional['OP']: pass


run = td.run

class _Matrix:
	vals: _T.List[float]
	rows: _T.List[_T.List[float]]
	cols: _T.List[_T.List[float]]

	def __init__(self, *values): pass

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
	def decompose(self) -> _T.Tuple[_T.Tuple]: pass

class _Position:
	x: int
	y: int
	z: int

	def __init__(self, *vals): pass

	def translate(self, x, y, z): pass

	def scale(self, x, y, z): pass

	def copy(self) -> '_Position': pass

	def __getitem__(self, item: int) -> float: pass
	def __setitem__(self, key, value): pass
	def __mul__(self, other: _T.Union[float, _Matrix]) -> _T.Union[float, '_Position']: pass
	def __add__(self, other: _T.Union[float, '_Position', '_Vector']) -> _T.Union[float, '_Position']: pass
	def __sub__(self, other: _T.Union[float, '_Position', '_Vector']) -> _T.Union[float, '_Position']: pass
	def __div__(self, other: float) -> '_Position': pass
	def __abs__(self) -> '_Position': pass
	def __neg__(self) -> '_Position': pass


class _Vector:
	x: float
	y: float
	z: float

	def __init__(self, *vals): pass

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

_OperableWithColor = _T.Union['_Color', _T.Tuple[float, float, float, float], _T.List[float], float]

class _Color:
	r: float
	g: float
	b: float
	a: float

	def __init__(self, *vals): pass

	def __abs__(self) -> '_Color': pass
	def __add__(self, other: _OperableWithColor) -> '_Color': pass
	def __sub__(self, other: _OperableWithColor) -> '_Color': pass
	def __mul__(self, other: _OperableWithColor) -> '_Color': pass
	def __floordiv__(self, other: _OperableWithColor) -> '_Color': pass
	def __truediv__(self, other: _OperableWithColor) -> '_Color': pass
	def __iadd__(self, other: _OperableWithColor) -> '_Color': pass
	def __isub__(self, other: _OperableWithColor) -> '_Color': pass
	def __imul__(self, other: _OperableWithColor) -> '_Color': pass
	def __ifloordiv__(self, other: _OperableWithColor) -> '_Color': pass
	def __itruediv__(self, other: _OperableWithColor) -> '_Color': pass
	def __radd__(self, other: _OperableWithColor) -> '_Color': pass
	def __rsub__(self, other: _OperableWithColor) -> '_Color': pass
	def __rmul__(self, other: _OperableWithColor) -> '_Color': pass
	def __rfloordiv__(self, other: _OperableWithColor) -> '_Color': pass
	def __rtruediv__(self, other: _OperableWithColor) -> '_Color': pass
	def __len__(self): return 4
	def __getitem__(self, item) -> float: pass
	def __setitem__(self, key, value): pass
	def __iter__(self): pass

class _ArcBall:
	def beginPan(self, u, v) -> None: pass
	def beginRotate(self, u, v) -> None: pass
	def beginDolly(self, u, v) -> None: pass
	def pan(self, u, v) -> None: pass
	def panTo(self, u, v, scale=1.0) -> None: pass
	def rotateTo(self, u, v, scale=1.0) -> None: pass
	def dolly(self, z) -> None: pass
	def dollyTo(self, u, v, scale=1.0) -> None: pass
	def transform(self) -> _Matrix: pass
	def setTransform(self, matrix: _Matrix) -> None: pass
	def identity(self) -> None: pass

class _PathInfo(str):
	path: str
	ext: str  # includes "."
	fileType: str
	absPath: str
	exists: bool
	isDir: bool
	isFile: bool

	# noinspection PyMissingConstructor,PyUnusedLocal
	def __init__(self, path: str = None): pass


class _Dependency:
	def __init__(self, _=None):
		self.val = None

	def modified(self): pass

class tdu:
	@staticmethod
	def legalName(s: str) -> str: pass

	@staticmethod
	def legalMenuName(s: str) -> str: pass

	# noinspection PyShadowingBuiltins
	@staticmethod
	def clamp(inputVal, min, max): pass

	@staticmethod
	def remap(inputVal, fromMin, fromMax, toMin, toMax): pass

	@staticmethod
	def rand(seed: _T.Any) -> float: pass

	@staticmethod
	def base(s: str) -> str: pass

	@staticmethod
	def digits(s: str) -> _T.Optional[int]: pass

	Dependency = _Dependency
	Position = _Position
	Vector = _Vector
	Color = _Color
	Matrix = _Matrix
	PathInfo = _PathInfo

	# noinspection PyShadowingBuiltins
	@staticmethod
	def split(string, eval=False) -> _T.List[str]: pass

	@staticmethod
	def match(pattern, inputList, caseSensitive=True) -> _T.List[str]: pass

	@staticmethod
	def collapsePath(path: str) -> str: pass

	@staticmethod
	def expandPath(path: str) -> str: pass

	ArcBall = _ArcBall

	fileTypes = {
		'audio': ['aif', 'aiff', 'flac', 'm4a', 'mp3', 'ogg', 'wav'],
		'channel': ['aif', 'aiff', 'bchan', 'bclip', 'chan', 'clip', 'csv', 'wav'],
		'component': ['tox'],
		'geometry': ['bhclassic', 'hclassic', 'obj', 'tog'],
		'image': ['bmp', 'dds', 'dpx', 'exr', 'ffs', 'fit', 'fits', 'gif', 'hdr', 'jpeg', 'jpg', 'pic', 'png', 'swf', 'tga', 'tif', 'tiff'],
		'midi': ['mid', 'midi'],
		'movie': ['3gp', 'avi', 'flv', 'm2ts', 'm4v', 'mkv', 'mov', 'mp4', 'mpeg', 'mpg', 'mts', 'mxf', 'r3d', 'ts', 'webm', 'wmv'],
		'object': ['3ds', 'abc', 'dae', 'dxf', 'fbx', 'obj', 'usd', 'usda', 'usdc'],
		'project': ['toe'],
		'text': ['csv', 'dat', 'frag', 'glsl', 'html', 'md', 'py', 'rtf', 'tsv', 'txt', 'vert', 'xml'],
		'material': ['sbsar'],
		'pointdata': ['csv', 'exr', 'fit', 'fits', 'obj', 'ply', 'pts', 'txt', 'xyz']}

class JustifyType(_E.Enum):
	TOPLEFT = 0
	TOPCENTER = 0
	TOPRIGHT = 0
	CENTERLEFT = 0
	CENTER = 0
	CENTERRIGHT = 0
	BOTTOMLEFT = 0
	BOTTOMCENTER = 0
	BOTTOMRIGHT = 0

class ParMode(_E.Enum):
	CONSTANT = 0
	EXPRESSION = 1
	EXPORT = 2
	BIND = 3

ExpandoStub = _Expando

class Cell(_T.SupportsInt, _T.SupportsAbs, _T.SupportsFloat, _T.SupportsBytes):
	val: str
	row: int
	col: int

	def offset(self, r: int, c: int) -> _T.Optional['Cell']: pass

_NameOrIndex = _T.Union[str, int, 'Cell', 'Channel']
_NamesOrIndices = _T.Iterable[_NameOrIndex]

class DAT(OP):
	def row(self, *nameorindex: _NameOrIndex, caseSensitive=True) -> _T.List[Cell]: pass
	def col(self, *nameorindex: _NameOrIndex, caseSensitive=True) -> _T.List[Cell]: pass
	def rows(self, *nameorindex: _NameOrIndex, caseSensitive=True) -> _T.List[_T.List[Cell]]: pass
	def cols(self, *nameorindex: _NameOrIndex, caseSensitive=True) -> _T.List[_T.List[Cell]]: pass
	def clear(self, keepSize=False, keepFirstRow=False, keepFirstCol=False): pass

	# noinspection PyMethodOverriding
	def copy(self, dat: 'DAT'): pass

	def appendRow(self, cells: _T.List[_T.Any], nameOrIndex: _NameOrIndex = None, sort: _NameOrIndex = None): pass
	def appendCol(self, cells: _T.List[_T.Any], nameOrIndex: _NameOrIndex = None, sort: _NameOrIndex = None): pass
	def appendRows(self, cells: _T.List[_T.List[_T.Any]], nameOrIndex: _NameOrIndex = None, sort: _NameOrIndex = None):
		pass
	def appendCols(self, cells: _T.List[_T.List[_T.Any]], nameOrIndex: _NameOrIndex = None, sort: _NameOrIndex = None):
		pass
	def insertRow(self, vals: _T.List[_T.Any], nameOrIndex: _NameOrIndex, sort=None) -> int: pass
	def insertCol(self, vals: _T.List[_T.Any], nameOrIndex: _NameOrIndex, sort=None) -> int: pass
	def replaceRow(self, nameOrIndex: _NameOrIndex, vals: _T.List[_T.Any], entireRow=True) -> int: pass
	def replaceCol(self, nameOrIndex: _NameOrIndex, vals: _T.List[_T.Any], entireCol=True) -> int: pass
	def deleteRow(self, nameOrIndex: _NameOrIndex): pass
	def deleteCol(self, nameOrIndex: _NameOrIndex): pass
	def deleteRows(self, vals: _NamesOrIndices): pass
	def deleteCols(self, vals: _NamesOrIndices): pass
	def setSize(self, numrows: int, numcols: int): pass
	def __getitem__(self, rowcol: _T.Tuple[_NameOrIndex, _NameOrIndex]) -> Cell: pass
	def __setitem__(self, rowcol: _T.Tuple[_NameOrIndex, _NameOrIndex], value): pass
	def cell(self, rowNameOrIndex: _NameOrIndex, colNameOrIndex: _NameOrIndex, caseSensitive=True) -> _T.Optional[Cell]:
		pass
	def cells(self, rowNameOrIndex: _NameOrIndex, colNameOrIndex: _NameOrIndex, caseSensitive=True) -> _T.List[Cell]: pass
	def findCell(
			self,
			pattern: str,
			rows: _T.Optional[_NamesOrIndices] = None,
			cols: _T.Optional[_NamesOrIndices] = None,
			valuePattern=True, rowPattern=True, colPattern=True, caseSensitive=False) -> _T.Optional[Cell]: pass
	def findCells(
			self,
			pattern: str,
			rows: _T.Optional[_NamesOrIndices] = None,
			cols: _T.Optional[_NamesOrIndices] = None,
			valuePattern=True, rowPattern=True, colPattern=True, caseSensitive=False) -> _T.List[Cell]: pass
	module: _T.Any
	numRows: int
	numCols: int
	text: str
	isTable: bool
	isText: bool
	locals: _T.Dict[str, _T.Any]

class oscoutDAT(DAT):
	def sendBytes(self, *messages) -> int: pass

	def sendOSC(
			self, *addressesFollowedByValueLists: _T.Union[str, _T.List[_T.Any]],
			asBundle=True, useNonStandardTypes=True, use64BitPrecision=False) -> int:
		pass

	def send(self, *messages: str, terminator='') -> int: pass

class CHOP(OP):
	numChans: int
	numSamples: int
	start: float
	end: float
	rate: float
	export: bool
	exportChanges: int
	isCHOP: bool
	isTimeSlice: bool

	def __getitem__(self, nameOrIndex: _NameOrIndex) -> 'Channel': pass
	def chan(self, *nameOrIndex: _NameOrIndex, caseSensitive=True) -> _T.Optional['Channel']: pass
	def chans(self, *nameOrIndex: _NameOrIndex, caseSensitive=True) -> _T.List['Channel']: pass
	def numpyArray(self) -> 'numpy.array': pass
	def convertToKeyframes(self, tolerance=0.1) -> 'animationCOMP': pass
	def save(self, filepath) -> str: pass

class COMP(OP):
	extensions: list
	extensionsReady: bool
	clones: _T.List['COMP']
	componentCloneImmune: bool
	vfs: '_VFS'
	dirty: bool
	externalTimeStamp: int
	currentChild: '_AnyOpT'
	selectedChildren: _T.List['_AnyOpT']
	pickable: bool
	isPrivate: bool
	isPrivacyActive: bool
	isPrivacyLicensed: bool
	privacyFirmCode: int
	privacyProductCode: int
	privacyDeveloperName: str
	privacyDeveloperEmail: str
	inputCOMPs: _T.List['_AnyCompT']
	outputCOMPs: _T.List['_AnyCompT']
	inputCOMPConnectors: _T.List['Connector']
	outputCOMPConnectors: _T.List['Connector']


	def destroyCustomPars(self): pass
	def sortCustomPages(self, *pages): pass
	def appendCustomPage(self, name: str) -> 'Page': pass
	def findChildren(
			self,
			type: _T.Type = None,
			path: str = None,
			depth: int = None,
			text: str = None,
			comment: str = None,
			maxDepth: int = 1,
			tags: _T.List[str] = None,
			allTags: _T.List[str] = None,
			parValue: str = None,
			parExpr: str = None,
			parName: str = None,
			onlyNonDefaults: bool = False,
			key: _T.Callable[['_AnyOpT'], bool] = None,
	) -> '_T.List[_AnyOpT]': pass
	def copy(self, o: '_AnyOpT', name=None) -> 'op': pass
	def create(self, OPtype: _T.Union[str, _T.Type['_AnyOpT']], name: str, initialize=True) -> '_AnyOpT': pass
	def collapseSelected(self): pass
	def copyOPs(self, listOfOPs: _T.List['_AnyOpT']) -> _T.List['_AnyOpT']: pass
	def initializeExtensions(self, index: int = None) -> _T.Any: pass
	def loadTox(self, filepath: str, unwired=False, pattern: str = None, password: str = None) -> 'OP': pass
	def resetNetworkView(self, recurse: bool = False): pass
	def save(self, filepath: str, createFolders: bool = False, password: str = None) -> 'str': pass
	def saveExternalTox(self, recruse: bool = False, password: str = None) -> int: pass
	def accessPrivateContents(self, key: str) -> bool: pass
	@_T.overload
	def addPrivacy(self, key: str, developerName: str = None): pass
	@_T.overload
	def addPrivacy(self, firmCode: int, productCode: int, developerName: str = None, developerEmail: str = None): pass
	def addPrivacy(self, *args, **kwargs): pass
	def blockPrivateContents(self, key: str): pass
	def removePrivacy(self, key: str) -> bool: pass
	def setVar(self, name: str, value): pass
	def unsetVar(self, name: str): pass
	def vars(self, *patterns: str) -> list: pass

Panel = _T.Any

class PanelCOMP(COMP):
	panel: Panel
	panelRoot: '_AnyOpT'
	panelChildren: _T.List['_AnyCompT']
	x: int
	y: int
	width: int
	height: int
	marginX: int
	marginY: int
	marginWidth: int
	marginHeight: int

	def panelParent(self, n: int = 1) -> _T.Optional['PanelCOMP']: pass
	def interactMouse(
			self,
			u, v,
			leftClick: int = 0, middleClick: int = 0, rightClick: int = 0,
			left=False, middle=False, right=False,
			wheel: float = 0, pixels=False, screen=False, quiet=True
	) -> 'PanelCOMP':
		pass

	def interactTouch(
			self,
			u, v,
			hover='id', start='id', move='id', end='id',
			pixels=False, screen=False, quiet=True, aux='data') -> 'PanelCOMP':
		pass
	def interactClear(self): pass
	def interactStatus(self) -> _T.List[list]: pass
	def locateMouse(self) -> _T.Tuple[float, float]: pass
	def locateMouseUV(self) -> _T.Tuple[float, float]: pass
	def setFocus(self, moveMouse=False): pass

class windowCOMP(COMP):
	scalingMonitorIndex: int
	isBorders: bool
	isFill: bool
	isOpen: bool
	width: int
	height: int
	x: int
	y: int
	contentX: int
	contentY: int
	contentWidth: int
	contentHeight: int

	def setForeground(self) -> bool: pass

class timeCOMP(COMP):
	frame: float
	seconds: float
	rate: float
	play: bool
	timecode: str
	start: float
	end: float
	rangeStart: float
	rangeEnd: float
	loop: bool
	independent: bool
	tempo: float
	signature1: int
	signature2: int

_AnyCompT = _T.Union[COMP, PanelCOMP, windowCOMP, timeCOMP]

_VFS = _T.Any
class Connector:
	index: int
	isInput: bool
	isOutput: bool
	inOP: '_AnyOpT'
	outOP: '_AnyOpT'
	owner: '_AnyOpT'
	connections: _T.List['Connector']

	def connect(self, target: _T.Union['_AnyOpT', 'Connector']): pass
	def disconnect(self): pass

_AttributeDataElementT = _T.Union[float, int, str]
_AttributeDataTupleT = _T.Union[
	_T.Tuple[_AttributeDataElementT],
	_T.Tuple[_AttributeDataElementT, _AttributeDataElementT],
	_T.Tuple[_AttributeDataElementT, _AttributeDataElementT, _AttributeDataElementT],
	_T.Tuple[_AttributeDataElementT, _AttributeDataElementT, _AttributeDataElementT, _AttributeDataElementT],
]
_AttributeDataT = _T.Union[
	_AttributeDataElementT,
	_AttributeDataTupleT,
	_Vector,
	_Position
]

class Attribute:
	owner: 'SOP'
	name: str
	size: int
	type: type
	default: _AttributeDataT

	def destroy(self): pass

class Attributes(_T.Collection[Attribute], _ABC):
	owner: 'SOP'

	def create(self, name: str, default: _AttributeDataT = None) -> Attribute: pass

class AttributeData(_AttributeDataTupleT):
	owner: 'SOP'
	val: _AttributeDataT

class Point(_T.Any):
	index: int
	owner: 'SOP'
	P: 'AttributeData'
	x: float
	y: float
	z: float

	def destroy(self): pass

class Points(_T.Sequence[Point], _ABC):
	owner: 'SOP'

class Vertex(_T.Any):
	index: int
	owner: 'SOP'
	point: Point
	prim: 'Prim'

class Prim(_T.Sized, _T.Sequence[Vertex], _T.Any, _ABC):
	center: _Position
	index: int
	normal: _Vector
	owner: 'SOP'
	weight: float
	direction: _Vector
	min: _Position
	max: _Position
	size: _Position

	def destroy(self, destroyPoints=True): pass
	def eval(self, u: float, v: float) -> _Position: pass

	def __getitem__(self, item: _T.Union[int, _T.Tuple[int, int]]) -> Vertex: pass

class Poly(Prim, _ABC):
	pass

class Bezier(Prim, _ABC):
	anchors: _T.List[Vertex]
	basis: _T.List[float]
	closed: bool
	order: float
	segments: _T.List[_T.List[Vertex]]
	tangents: _T.List[_T.Tuple[Vertex, Vertex]]

	def insertAnchor(self, u: float) -> Vertex: pass
	def updateAnchor(self, anchorIndex: int, targetPosition: _Position, tangents=True) -> _Position: pass
	def appendAnchor(self, targetPosition: _Position, preserveShape=True) -> Vertex: pass
	def updateTangent(
			self, tangentIndex: int, targetPosition: _Position,
			rotate=True, scale=True, rotateLock=True, scaleLock=True) -> _Position: pass
	def deleteAnchor(self, anchorIndex: int): pass

class Mesh(Prim, _ABC):
	closedU: bool
	closedV: bool
	numRows: int
	numCols: int

class Prims(_T.Sequence[Prim], _ABC):
	owner: 'SOP'

class SOP(OP):
	compare: bool
	template: bool
	points: Points
	prims: Prims
	numPoints: int
	numPrims: int
	pointAttribs: Attributes
	primAttribs: Attributes
	vertexAttribs: Attributes
	center: _Position
	min: _Position
	max: _Position
	size: _Position

	def save(self, filepath: str) -> str: pass

class scriptSOP(SOP):
	def destroyCustomPars(self): pass
	def sortCustomPages(self, *pages): pass
	def appendCustomPage(self, name: str) -> 'Page': pass
	def clear(self): pass
	# noinspection PyMethodOverriding
	def copy(self, chop: CHOP): pass
	def appendPoint(self) -> Point: pass
	def appendPoly(self, numVertices: int, closed=True, addPoints=True) -> Poly: pass
	def appendBezier(self, numVertices: int, closed=True, order=4, addPoints=True) -> Bezier: pass
	def appendMesh(self, numROws: int, numCols: int, closedU=False, closedV=False, addPoints=True) -> Mesh: pass

class TOP(OP):
	width: int
	height: int

	def save(self, path): pass

class MAT(OP): pass

_AnyOpT = _T.Union[OP, DAT, COMP, CHOP, SOP, MAT, '_AnyCompT']

baseCOMP = COMP
panelCOMP = PanelCOMP
evaluateDAT = mergeDAT = nullDAT = parameterexecuteDAT = parameterDAT = tableDAT = textDAT = scriptDAT = DAT
parameterCHOP = nullCHOP = selectCHOP = inCHOP = outCHOP = CHOP
animationCOMP = COMP
inTOP = outTOP = TOP
importselectSOP = SOP

class objectCOMP(COMP):
	localTransform: _Matrix
	worldTransform: _Matrix
	def transform(self) -> _Matrix: pass
	def setTransform(self, matrix: _Matrix): pass
	def preTransform(self) -> _Matrix: pass
	def setPreTransform(self, matrix: _Matrix): pass
	def relativeTransform(self, target: COMP) -> _Matrix: pass
	def importABC(self, filepath, lights=True, cameras=True, mergeGeometry=True, gpuDeform=True, rate=None, textureFolder=None, geometryFolder=None, animationFolder=None): pass
	def importFBX(self, filepath, lights=True, cameras=True, mergeGeometry=True, gpuDeform=True, rate=None, textureFolder=None, geometryFolder=None, animationFolder=None): pass

class cameraCOMP(objectCOMP):
	def projectionInverse(self, x, y) -> _Matrix: pass
	def projection(self, x, y) -> _Matrix: pass

class scriptCHOP(CHOP):
	def destroyCustomPars(self): pass
	def sortCustomPages(self, *pages): pass
	def clear(self): pass
	def appendCustomPage(self, name: str) -> 'Page': pass
	# noinspection PyMethodOverriding
	def copy(self, chop: CHOP): pass
	def appendChan(self, name: str) -> 'Channel': pass

class timerCHOP(CHOP):
	beginFrame: _T.List[_T.Any]
	beginSample: _T.List[_T.Any]
	beginSeconds: _T.List[_T.Any]
	cycle: float
	fraction: float
	runningFraction: float
	runningFrame: float
	runningLengthFrames: float
	runningLengthSamples: float
	runningLengthSeconds: float
	runningLengthTimecode: str  # format 00:00:00.00
	runningSample: float
	runningSeconds: float
	runningTimecode: str  # format 00:00:00.00
	segment: float

	def goToNextSegment(self): pass
	def goToCycleEnd(self): pass
	def goTo(
			self,
			segment: float = None,
			cycle: float = None, endOfCycle=True,
			seconds: float = None, frame: float = None, sample: float = None, fraction: float = None):
		pass
	def goToPrevSegment(self): pass
	def lastCycle(self): pass


class App:
	name: str
	build: str
	launchTime: str
	product: str
	version: str
	osName: str
	osVersion: str
	userPaletteFolder: str

app: App

class RenderPickEvent(tuple):
	u: float
	v: float
	select: bool
	selectStart: bool
	selectEnd: bool
	pickOp: OP
	pos: _Position
	texture: _Position
	color: _T.Tuple[float, float, float, float]
	normal: _Vector
	depth: float
	instanceId: int

def debug(*args):
	pass

root = baseCOMP()
absTime = timeCOMP()

me = None  # type: _AnyOpT
