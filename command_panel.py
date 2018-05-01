from inspect import signature
import os

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

	@staticmethod
	def resolveOP(o):
		if isinstance(o, str):
			return op(o)
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

	@staticmethod
	def getActiveEditor():
		pane = ui.panes.current
		if pane.type == PaneType.NETWORKEDITOR:
			return pane
		for pane in ui.panes:
			if pane.type == PaneType.NETWORKEDITOR:
				return pane

	def navigateTo(self, o):
		o = self.resolveOP(o)
		if not o:
			return
		pane = self.getActiveEditor()
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
			return
		if path is None:
			if o.isDAT and hasattr(o.par, 'writepulse'):
				o.par.writepulse.pulse()
				return
			if o.isCOMP:
				path = o.par.externaltox.eval()
			elif hasattr(o.par, 'file'):
				path = o.par.file.eval()
		if not path:
			return
		o.save(path)

	def reloadOPFile(self, o):
		o = self.resolveOP(o)
		if not o:
			return
		if o.isDAT and hasattr(o.par, 'loadonstartpulse'):
			o.par.loadonstartpulse.pulse()
			return
		if o.isCOMP:
			o.par.reinitnet.pulse()

class Command:
	def __init__(self, action, label=None, help=None):
		self.action = action
		self.label = label
		self.help = help

	def invoke(self, context):
		if len(signature(self.action).parameters) >= 1:
			self.action(context)
		else:
			self.action()

	@classmethod
	def forOpenUI(cls, o, unique=True, borders=True, **kwargs):
		return cls(lambda context: context.openUI(o, unique=unique, borders=borders), **kwargs)

	@classmethod
	def forToggleUI(cls, o, borders=True, **kwargs):
		return cls(lambda context: context.openOrToggleUI(o, borders=borders), **kwargs)

	@classmethod
	def forEdit(cls, o, **kwargs):
		return cls(lambda context: context.navigateTo(o), **kwargs)

	@classmethod
	def forParams(cls, oppath, **kwargs):
		def _action(context):
			o = context.resolveOP(oppath)
			if o:
				o.openParameters()
		return cls(_action, **kwargs)

	@classmethod
	def forReload(cls, oppaths, **kwargs):
		def _action(context):
			targetops = ops(oppaths)
			for o in targetops:
				context.reloadOPFile(o)
		return cls(_action, **kwargs)

	@classmethod
	def forSave(cls, oppaths, path, **kwargs):
		def _action(context):
			targetops = ops(oppaths)
			for o in targetops:
				context.saveOP(o, path)
		return cls(_action, **kwargs)

	@classmethod
	def forExec(
			cls, oppath, args=None, endFrame=False, fromOP=None, group=None, delayFrames=0, delayMilliSeconds=0, **kwargs):
		def _action(context):
			o = context.resolveOP(oppath)
			if o and o.isDAT:
				o.run(
					*args,
					endFrame=endFrame, fromOP=fromOP, group=group,
					delayFrames=delayFrames, delayMilliSeconds=delayMilliSeconds)
		return cls(_action, **kwargs)

	@classmethod
	def forAction(cls, action, **kwargs):
		return cls(action, **kwargs)

	@classmethod
	def fromRow(cls, dat, row):
		typename = dat[row, 'type']
		label = str(dat[row, 'label'] or '')
		helptext = str(dat[row, 'help'] or '')
		kwargs = {
			'label': label,
			'help': helptext,
		}
		o = str(dat[row, 'op'] or '')
		if typename in ['open', 'show', 'view']:
			return Command.forOpenUI(
				o,
				unique=dat[row, 'unique'] == '1',
				borders=dat[row, 'borders'] == '1',
				**kwargs)
		elif typename in ['toggle']:
			return Command.forToggleUI(
				o,
				borders=dat[row, 'borders'] == '1',
				**kwargs)
		elif typename in ['params', 'pars']:
			return Command.forParams(o, **kwargs)
		elif typename in ['edit', 'nav', 'navigate']:
			return Command.forEdit(o, **kwargs)
		elif typename in ['run']:
			return Command.forExec(
				o,
				delayFrames=int(dat[row, 'delayFrames'] or 0),
				**kwargs)
		elif typename in ['code', 'script']:
			code = str(dat[row, 'code'] or '')
			if not code:
				return None
			if code.startswith('lambda'):
				return Command.forAction(eval(code), **kwargs)
			else:
				return Command.forAction(lambda _: eval(code), **kwargs)
		elif typename in ['reload']:
			return Command.forReload(o, **kwargs)
		elif typename in ['save']:
			return Command.forSave(
				o,
				path=dat[row, 'path'] or dat[row, 'file'],
				**kwargs)


def loadCommandsFromTable(dat):
	commands = []
	for row in range(1, dat.numRows):
		command = Command.fromRow(dat, row)
		if command:
			commands.append(command)
	return commands

# ... not sure if i'm going to be using this list stuff yet


# me - this DAT
#
# comp - the List Component that holds this panel
# row - the row number of the cell being updated
# col - the column number of the cell being updated
#
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


def _updateCellColor(attribs):
	if attribs.select:
		attribs.bgColor = activebgcolor
	elif attribs.rollover:
		attribs.bgColor = hoverbgcolor
	else:
		attribs.bgColor = defaultbgcolor

class ListCallbacks:

	# called when Reset parameter is pulsed, or on load
	@staticmethod
	def onInitCell(comp, row, col, attribs):
		_updateCellColor(attribs)
		return

	@staticmethod
	def onInitRow(comp, row, attribs):
		return

	@staticmethod
	def onInitCol(comp, col, attribs):
		return

	@staticmethod
	def onInitTable(comp, attribs):
		return

	# called during specific events
	#
	# coords - a named tuple containing the following members:
	#   x
	#   y
	#   u
	#   v
	@staticmethod
	def onRollover(comp, row, col, coords, prevRow, prevCol, prevCoords):
		return

	@staticmethod
	def onSelect(comp, startRow, startCol, startCoords, endRow, endCol, endCoords, start, end):
		return

	@staticmethod
	def onRadio(comp, row, col, prevRow, prevCol):
		return

	@staticmethod
	def onFocus(comp, row, col, prevRow, prevCol):
		return

	@staticmethod
	def onEdit(comp, row, col, val):
		return

	# return True if interested in this drop event, False otherwise
	@staticmethod
	def onHoverGetAccept(comp, row, col, coords, prevRow, prevCol, prevCoords, dragItems):
		return False

	@staticmethod
	def onDropGetAccept(comp, row, col, coords, prevRow, prevCol, prevCoords, dragItems):
		return False

