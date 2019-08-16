from inspect import signature
import os
from math import ceil

if False:
	class _Dummy:
		pass
	JustifyType = _Dummy()
	ui = _Dummy()
	PaneType = _Dummy()
	def op(path): return _Dummy()
	def ops(path): return []
	del _Dummy

class Context:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	def resolveOP(self, o):
		if isinstance(o, str):
			return self.ownerComp.op(o)
		return o

	def openUI(self, o, unique=True, borders=True):
		o = self.resolveOP(o)
		if not o:
			return
		if o.type == 'window':
			o.par.winopen.pulse()
		else:
			o.openViewer(unique=unique, borders=borders)

	def closeUI(self, o, topMost=False):
		o = self.resolveOP(o)
		if not o:
			return
		if o.type == 'window':
			o.par.winclose.pulse()
		else:
			o.closeViewer(topMost=topMost)

	def openOrToggleUI(self, o, borders=True):
		o = self.resolveOP(o)
		if not o:
			return
		if o.type == 'window':
			self.toggleUI(o, borders=borders)
		else:
			self.openUI(o, unique=True, borders=borders)

	def toggleUI(self, o, borders=True):
		o = self.resolveOP(o)
		if not o:
			return
		if o.type == 'window':
			if o.isOpen:
				self.openUI(o, unique=True, borders=borders)
			else:
				self.closeUI(o, topMost=False)
		else:
			raise NotImplementedError('toggleUI only supported for Window COMP')

	@property
	def activeEditor(self):
		pane = ui.panes.current
		if pane.type == PaneType.NETWORKEDITOR:
			return pane
		for pane in ui.panes:
			if pane.type == PaneType.NETWORKEDITOR:
				return pane

	def getSelectedOps(self, predicate=None):
		pane = self.activeEditor
		if not pane:
			return []
		sel = pane.owner.selectedChildren or [pane.owner.currentChild]
		if predicate is not None:
			sel = list(filter(predicate, sel))
		return sel

	def getSelectedOrContext(self, predicate):
		sel = self.getSelectedOps(predicate)
		if sel:
			return sel[0]
		pane = self.activeEditor
		if not pane:
			return
		o = pane.owner
		while o:
			if predicate(o):
				return o
			o = o.parent()

	def navigateTo(self, o):
		o = self.resolveOP(o)
		if not o:
			return
		pane = self.activeEditor
		if pane:
			pane.owner = o

	def openNetwork(self, o):
		o = self.resolveOP(o)
		if not o or not o.isCOMP:
			return
		pane = ui.panes.createFloating(type=PaneType.NETWORKEDITOR)
		pane.owner = o

	@staticmethod
	def resolveFile(path):
		return path if os.path.exists(path) else ''

	def saveOP(self, o, path=None):
		o = self.resolveOP(o)
		if not o:
			return False
		if path is None:
			if o.isDAT and getattr(o.par, 'file') and hasattr(o.par, 'writepulse'):
				path = o.par.file
				o.par.writepulse.pulse()
				ui.status = 'saved {} to {}'.format(o.path, path)
				return True
			if o.isCOMP:
				path = o.par.externaltox.eval()
			elif hasattr(o.par, 'file'):
				path = o.par.file.eval()
		if not path:
			return False
		o.save(path)
		ui.status = 'saved {} to {}'.format(o.path, path)
		return True

	def reloadOPFile(self, o):
		o = self.resolveOP(o)
		if not o:
			return False
		if o.isDAT and hasattr(o.par, 'loadonstartpulse'):
			o.par.loadonstartpulse.pulse()
			return True
		if o.isCOMP:
			o.par.reinitnet.pulse()
			return True
		return False

class Command:
	def __init__(self, name, action, **attrs):
		self.name = str(name)
		self.action = action
		self.attrs = attrs or {}

	@property
	def label(self): return self.attrs.get('label') or self.name

	@property
	def help(self): return self.attrs.get('help') or ''

	@property
	def img(self):
		i = self.attrs.get('img')
		if isinstance(i, str):
			i = op(i)
		return i

	def invoke(self, context):
		if len(signature(self.action).parameters) >= 1:
			self.action(context)
		else:
			self.action()

	@classmethod
	def forOpenUI(cls, name, o, unique=True, borders=True, **kwargs):
		return cls(name, lambda context: context.openUI(o, unique=unique, borders=borders), **kwargs)

	@classmethod
	def forToggleUI(cls, name, o, borders=True, **kwargs):
		return cls(name, lambda context: context.openOrToggleUI(o, borders=borders), **kwargs)

	@classmethod
	def forEdit(cls, name, o, **kwargs):
		return cls(name, lambda context: context.navigateTo(o), **kwargs)

	@classmethod
	def forParams(cls, name, oppath, **kwargs):
		def _action(context):
			o = context.resolveOP(oppath)
			if o:
				o.openParameters()
		return cls(name, _action, **kwargs)

	@classmethod
	def forReload(cls, name, oppaths, **kwargs):
		def _action(context):
			targetops = ops(oppaths)
			for o in targetops:
				context.reloadOPFile(o)
		return cls(name, _action, **kwargs)

	@classmethod
	def forSave(cls, name, oppaths, path, **kwargs):
		def _action(context):
			targetops = ops(oppaths)
			for o in targetops:
				context.saveOP(o, path)
		return cls(name, _action, **kwargs)

	@classmethod
	def forExec(
			cls, name, oppath, args=None, endFrame=False, fromOP=None,
			group=None, delayFrames=0, delayMilliSeconds=0, **kwargs):
		def _action(context):
			o = context.resolveOP(oppath)
			if o and o.isDAT:
				o.run(
					*args,
					endFrame=endFrame, fromOP=fromOP, group=group,
					delayFrames=delayFrames, delayMilliSeconds=delayMilliSeconds,
					**kwargs)
		return cls(name, _action, **kwargs)

	@classmethod
	def forAction(cls, name, action, **kwargs):
		return cls(name, action, **kwargs)

	@classmethod
	def fromRow(cls, dat, row):
		obj = {
			dat[0, i].val: dat[row, i].val
			for i in range(dat.numCols)
		}
		return Command.fromObj(obj)

	@classmethod
	def fromObj(cls, obj):
		if _asbool(obj.get('hidden'), False):
			return None
		name = obj['name']
		typename = obj.get('type')
		attrs = {
			'label': obj.get('label'),
			'help': obj.get('help'),
			'img': obj.get('img'),
		}
		o = obj.get('o') or obj.get('op')
		if not typename:
			action = obj.get('action', _noop)
			return Command.forAction(name, action, **attrs)
		if typename in ['open', 'show', 'view']:
			return Command.forOpenUI(
				name, o,
				unique=_asbool(obj.get('unique'), False),
				borders=_asbool(obj.get('borders'), False),
				**attrs)
		elif typename in ['toggle']:
			return Command.forToggleUI(
				name, o,
				borders=_asbool(obj.get('borders'), False),
				**attrs)
		elif typename in ['params', 'pars']:
			return Command.forParams(name, o, **attrs)
		elif typename in ['edit', 'nav', 'navigate']:
			return Command.forEdit(name, o, **attrs)
		elif typename in ['run']:
			return Command.forExec(
				name, o,
				delayFrames=_asint(obj.get('delayFrames'), 0),
				**attrs)
		elif typename in ['code', 'script']:
			code = obj.get('code')
			if not code:
				return Command.forAction(name, _noop, **attrs)
			if code.startswith('lambda'):
				return Command.forAction(name, eval(code), **attrs)
			else:
				return Command.forAction(name, lambda _: eval(code), **attrs)
		elif typename in ['reload']:
			return Command.forReload(name, o, **attrs)
		elif typename in ['save']:
			return Command.forSave(
				name, o,
				path=obj.get('path') or obj.get('file'),
				**attrs)

def _noop(*args, **kwargs):
	pass

def _asbool(val, defval):
	if val is None or val == '':
		return defval
	if val == '1':
		return True
	if val == '0':
		return False
	return bool(val)

def _asint(val, defval):
	if val is None or val == '':
		return defval
	return int(val)

def _strornull(val):
	return str(val) if val is not None else None

class CommandPanel:
	def __init__(self, comp):
		self.ownerComp = comp
		self.commandlist = []
		self.commandlookup = {}

	def _AddCommand(self, command):
		if command:
			self.commandlist.append(command)
			self.commandlookup[command.name] = command

	def _AddCommands(self, commands):
		if commands:
			for command in commands:
				self._AddCommand(command)

	def _AddCommandsFromTable(self, dat):
		if not dat or dat.numRows < 2:
			return
		for row in range(1, dat.numRows):
			self._AddCommand(Command.fromRow(dat, row))

	def RebuildCommands(self):
		self.commandlist.clear()
		self.commandlookup.clear()
		self._AddCommandsFromTable(self.ownerComp.op('./command_table_in'))
		if self.ownerComp.par.Includebasictoolcmds:
			self._AddCommands(_basicToolCommands)
		if self.ownerComp.par.Includetestcmds:
			self._AddCommandsFromTable(self.ownerComp.op('./TEST_commands'))

		cmdobjs = self.ownerComp.par.Cmdobjs.eval()
		if cmdobjs:
			if isinstance(cmdobjs, (list, tuple)):
				for cmdobj in cmdobjs:
					self._AddCommand(Command.fromObj(cmdobj))
			else:
				self._AddCommand(Command.fromObj(cmdobjs))

	def BuildCommandTable(self, dat):
		self.RebuildCommands()
		dat.clear()
		dat.appendRow(['name', 'label', 'help'])
		for command in self.commandlist:
			dat.appendRow([
				command.name,
				command.label,
				command.help,
			])

	@property
	def IsHorizontal(self):
		return self.ownerComp.par.Layout == 'horz'

	@property
	def LayoutRows(self):
		n = len(self.commandlist)
		linemax = self.ownerComp.par.Maxperline.eval()
		if n == 0:
			return 0
		if self.IsHorizontal:
			if linemax == 0:
				return 1
			else:
				return ceil(n / linemax)
		else:
			if linemax == 0:
				return n
			else:
				return linemax

	@property
	def LayoutCols(self):
		n = len(self.commandlist)
		linemax = self.ownerComp.par.Maxperline.eval()
		if n == 0:
			return 0
		if self.IsHorizontal:
			if linemax == 0:
				return n
			else:
				return linemax
		else:
			if linemax == 0:
				return 1
			else:
				return ceil(n / linemax)

	def _GetCellCommand(self, listComp, row, col):
		if self.IsHorizontal:
			i = (row * listComp.par.cols) + col
		else:
			i = (col * listComp.par.rows) + row
		return self.commandlist[i] if i < len(self.commandlist) else None

	# called when Reset parameter is pulsed, or on load
	def List_onInitCell(self, listComp, row, col, attribs):
		command = self._GetCellCommand(listComp, row, col)
		if not command:
			attribs.text = ''
			attribs.topBorderOutColor = attribs.bottomBorderOutColor = 0, 0, 0, 0
			attribs.rightBorderOutColor = attribs.leftBorderOutColor = 0, 0, 0, 0
			attribs.bgColor = 0, 0, 0, 0
		else:
			attribs.text = command.label
			attribs.help = command.help
			attribs.top = command.img
			attribs.topBorderOutColor = attribs.bottomBorderOutColor = cellbordercolor
			attribs.rightBorderOutColor = attribs.leftBorderOutColor = cellbordercolor
			self.UpdateCellState(listComp, row, col)

	def List_onInitRow(self, listComp, row, attribs):
		attribs.rowHeight = listComp.height / listComp.par.rows

	def List_onInitCol(self, listComp, col, attribs):
		attribs.colWidth = listComp.width / listComp.par.cols

	def List_onInitTable(self, listComp, attribs):
		self.UpdateAllCellStates(listComp)

	# called during specific events
	#
	# coords - a named tuple containing the following members:
	#   x
	#   y
	#   u
	#   v
	def List_onRollover(self, listComp, row, col, coords, prevRow, prevCol, prevCoords):
		self.UpdateAllCellStates(listComp)

	def List_onSelect(self, listComp, startRow, startCol, startCoords, endRow, endCol, endCoords, start, end):
		self.UpdateAllCellStates(listComp)
		if not start:
			return
		command = self._GetCellCommand(listComp, startRow, startCol)
		if not command:
			return
		context = Context(self.ownerComp)
		command.invoke(context)
		return

	def List_onRadio(self, listComp, row, col, prevRow, prevCol):
		return

	def List_onFocus(self, listComp, row, col, prevRow, prevCol):
		return

	def List_onEdit(self, listComp, row, col, val):
		return

	# return True if interested in this drop event, False otherwise
	def List_onHoverGetAccept(self, listComp, row, col, coords, prevRow, prevCol, prevCoords, dragItems):
		return False

	def List_onDropGetAccept(self, listComp, row, col, coords, prevRow, prevCol, prevCoords, dragItems):
		return False

	def UpdateAllCellStates(self, listComp):
		for r in range(listComp.par.rows.eval()):
			for c in range(listComp.par.cols.eval()):
				self.UpdateCellState(listComp, r, c)

	def UpdateCellState(self, listComp, row, col):
		command = self._GetCellCommand(listComp, row, col)
		if not command:
			return
		attribs = listComp.cellAttribs[row, col]
		if listComp.panel.select and row == listComp.selectRow and col == listComp.selectCol:
			attribs.bgColor = activebgcolor
		elif listComp.panel.rollover and row == listComp.rolloverRow and col == listComp.rolloverCol:
			attribs.bgColor = hoverbgcolor
		else:
			attribs.bgColor = defaultbgcolor


# attribs contains the following members:
#
# text				   str            cell contents
# help                 str       	  help text
#
# textColor            r g b a        font color
# textOffsetX		   n			  horizontal text offset
# textOffsetY		   n			  vertical text offset
# textJustify		   m			  m is one of:  JustifyType.TOPLEFT, JustifyType.TOPCENTER,
#													JustifyType.TOPRIGHT, JustifyType.CENTERLEFT,
#													JustifyType.CENTER, JustifyType.CENTERRIGHT,
#													JustifyType.BOTTOMLEFT, JustifyType.BOTTOMCENTER,
#													JustifyType.BOTTOMRIGHT
#
# bgColor              r g b a        background color
#
# leftBorderInColor	   r g b a		  inside left border color
# rightBorderInColor   r g b a		  inside right border color
# bottomBorderInColor  r g b a		  inside bottom border color
# topBorderInColor	   r g b a		  inside top border color
#
# leftBorderOutColor   r g b a		  outside left border color
# rightBorderOutColor  r g b a		  outside right border color
# bottomBorderOutColor r g b a		  outside bottom border color
# topBorderOutColor	   r g b a		  outside top border color
#
# colWidth             w              sets column width
# colStetch            True/False     sets column stretchiness (width is min width)
# rowHeight            h              sets row height
# rowIndent            w              offsets entire row by this amount
#
# editable			   int			  number of clicks to activate editing the cell.
# draggable             True/False     allows cell to be drag/dropped elsewhere
# fontBold             True/False     render font bolded
# fontItalic           True/False     render font italicized
# fontSizeX            float		  font X size in pixels
# fontSizeY            float		  font Y size in pixels, if not specified, uses X size
# fontFace             str			  font face, example 'Verdana'
# wordWrap             True/False     word wrap
#
# top                  TOP			  background TOP operator
#
# select   true when the cell/row/col is currently being selected by the mouse
# rollover true when the mouse is currently over the cell/row/col
# radio    true when the cell/row/col was last selected
# focus    true when the cell/row/col is being edited
#
# currently not implemented:
#
# type                str             cell type: 'field' or 'label'
# fieldtype           str             field type: 'float' 'string' or  'integer'
# setpos              True/False x y  set cell absolute when first argument is True
# padding             l r b t         cell padding from each edge, expressed in pixels
# margin              l r b t         cell margin from neighbouring cells, expressed in pixels
#
# fontpath            path            File location to font. Don't use with 'font'
# fontformat          str             font format: 'polygon', 'outline' or 'bitmap'
# fontantialiased     True/False      render font antialiased
# fontcharset         str             font character set
#
# textjustify         h v             left/right/center top/center/bottom
# textoffset          x y             text position offset
#

defaultbgcolor = 0.3, 0.3, 0.3, 1
hoverbgcolor = 0.7, 0.7, 0.7, 1
activebgcolor = 0.9, 0.9, 0.9, 1

cellbordercolor = 0.9, 0.9, 0.9, 1

def _copyPaths(context: Context):
	sel = context.getSelectedOps()
	ui.clipboard = ' '.join([o.path for o in sel])

def _saveTox(context: Context):
	comp = context.getSelectedOrContext(lambda o: o.isCOMP and o.par.externaltox)
	if comp:
		context.saveOP(comp)

_basicToolCommands = [
	Command.forAction(
		'tools-copy-path',
		_copyPaths,
		label='copy path',
		help='copy paths of selected ops'),
	Command.forAction(
		'tools-save-tox',
		_saveTox,
		label='save',
		help='save selected or active component tox file'),
]
