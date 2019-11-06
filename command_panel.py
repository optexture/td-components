from inspect import signature
import os

if False:
	from _stubs import *

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

def _callWithOptionalParam(fn, param):
	if len(signature(fn).parameters) == 0:
		return fn()
	else:
		return fn(param)

class Command:
	def __init__(self, action, **attrs):
		self.action = action
		self.attrs = attrs or {}

	@property
	def label(self): return self.attrs.get('label') or '--'

	@property
	def help(self): return self.attrs.get('help') or ''

	@property
	def img(self):
		i = self.attrs.get('img')
		return op(i) if isinstance(i, str) else i

	@property
	def isIcon(self):
		return self.attrs.get('isIcon')

	def invoke(self, context):
		_callWithOptionalParam(self.action, context)

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
			cls, oppath, args=None, endFrame=False, fromOP=None,
			group=None, delayFrames=0, delayMilliSeconds=0, **kwargs):
		def _action(context):
			o = context.resolveOP(oppath)
			if o and o.isDAT:
				o.run(
					*args,
					endFrame=endFrame, fromOP=fromOP, group=group,
					delayFrames=delayFrames, delayMilliSeconds=delayMilliSeconds,
					**kwargs)
		return cls(_action, **kwargs)

	@classmethod
	def forScriptDAT(cls, dat):
		if 'def action' not in dat.text:
			return cls.forExec(dat.path, label=dat.name)
		else:
			locs = dat.locals
			return cls(
				lambda context: _callWithOptionalParam(dat.module.action, context),
				label=locs.get('label', None) or dat.name,
				**{
					k: locs[k]
					for k in ['img', 'help', 'isIcon']
					if k in locs
				})

	@classmethod
	def forAction(cls, action, **kwargs):
		return cls(action, **kwargs)

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
		typename = obj.get('type')
		attrs = {
			'label': obj.get('label'),
			'help': obj.get('help'),
			'img': obj.get('img'),
			'isIcon': obj.get('isIcon'),
		}
		o = obj.get('op')
		if not typename and 'script' in obj:
			typename = 'script'
		if not typename:
			action = obj.get('action', _noop)
			return Command.forAction(action, **attrs)
		if typename in ['open', 'view']:
			return Command.forOpenUI(
				o,
				unique=_asbool(obj.get('unique'), True),
				borders=_asbool(obj.get('borders'), True),
				**attrs)
		elif typename in ['toggle']:
			return Command.forToggleUI(
				o,
				borders=_asbool(obj.get('borders'), False),
				**attrs)
		elif typename in ['pars']:
			return Command.forParams(o, **attrs)
		elif typename in ['edit', 'navigate']:
			return Command.forEdit(o, **attrs)
		elif typename in ['run']:
			return Command.forExec(
				o,
				delayFrames=_asint(obj.get('delayFrames'), 0),
				**attrs)
		elif typename == 'script':
			code = obj.get('script')
			if not code:
				return Command.forAction(_noop, **attrs)
			if code.startswith('lambda'):
				return Command.forAction(eval(code), **attrs)
			else:
				return Command.forAction(lambda _: eval(code), **attrs)
		elif typename in ['reload']:
			return Command.forReload(o, **attrs)
		elif typename in ['save']:
			return Command.forSave(
				o,
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

	def _AddCommand(self, command):
		if command:
			self.commandlist.append(command)

	def _AddCommands(self, commands):
		if commands:
			for command in commands:
				self._AddCommand(command)

	def _AddCommandsFromTable(self, dat):
		if not dat or dat.numRows < 2:
			return
		for row in range(1, dat.numRows):
			self._AddCommand(Command.fromRow(dat, row))

	def _AddCommandsFromScriptDATs(self):
		scripts = self.ownerComp.par.Cmdscripts.evalOPs()
		for script in scripts:
			self._AddCommand(Command.forScriptDAT(script))

	def _AddCommandsFromList(self):
		cmdobjs = self.ownerComp.par.Cmdobjs.eval()
		if cmdobjs:
			if isinstance(cmdobjs, (list, tuple)):
				for cmdobj in cmdobjs:
					self._AddCommand(Command.fromObj(cmdobj))
			else:
				self._AddCommand(Command.fromObj(cmdobjs))

	def RebuildCommands(self):
		self.commandlist.clear()
		self._AddCommandsFromTable(self.ownerComp.op('./command_table_in'))
		if self.ownerComp.par.Includebasictoolcmds:
			self._AddCommands(_basicToolCommands)
		if self.ownerComp.par.Includetestcmds:
			self._AddCommandsFromTable(self.ownerComp.op('./TEST_commands'))
		self._AddCommandsFromList()
		self._AddCommandsFromScriptDATs()

	def BuildCommandTable(self, dat):
		self.RebuildCommands()
		dat.clear()
		dat.appendRow(['label', 'help', 'img', 'isIcon'])
		for command in self.commandlist:
			dat.appendRow([
				command.label,
				command.help,
				command.img or '',
				bool(command.isIcon),
			])

	def _GetCommandByIndex(self, index):
		if index < 0 or index >= len(self.commandlist):
			return None
		return self.commandlist[index]

	def ExecuteCommandByIndex(self, index):
		command = self._GetCommandByIndex(index)
		if not command:
			return
		context = Context(self.ownerComp)
		command.invoke(context)

	def InitializeButton(self, button, index):
		command = self._GetCommandByIndex(index)  # type: Command
		button.par.display = True
		button.par.Buttonofflabel = command.label
		button.par.Buttononlabel = command.label
		button.par.Offtoonscript0 = 'iop.commands.ExecuteCommandByIndex({})'.format(index)
		img = command.img
		imgpath = img.path if img is not None else ''
		button.par.Buttonofftop = imgpath
		button.par.Buttonontop = imgpath
		button.par.Popuphelp = command.help
		if command.isIcon and not img:
			button.par.Buttonfont = 'Material_Design_Icons'

def _copyPaths(context: Context):
	sel = context.getSelectedOps()
	ui.clipboard = ' '.join([o.path for o in sel])

def _saveTox(context: Context):
	comp = context.getSelectedOrContext(lambda o: o.isCOMP and o.par.externaltox)
	if comp:
		context.saveOP(comp)

def _incrementComponentVersion(context: Context):
	comp = context.getSelectedOrContext(lambda o: o.isCOMP and hasattr(o.par, 'Compversion'))
	print('OMG increment comp version... trying {}'.format(comp))
	if not comp:
		comp = context.getSelectedOrContext(lambda o: o.isCOMP)
		print('OMG increment comp version did not find comp, trying {}'.format(comp))
	if not comp:
		ui.status = 'Unable to increment component version, no suitable COMP'
		return
	ui.status = 'Updating component version of {!r}'.format(comp)
	if not hasattr(comp.par, 'Compversion'):
		page = comp.appendCustomPage(':meta')
		par = page.appendInt('Compversion', label=':Version')[0]
		par.val = 0
		par.default = 0
		par.readOnly = True
	else:
		par = comp.par.Compversion
		par.val += 1
		par.default = par.val
		if par.normMax < par.val:
			par.normMax = par.val
		par.readOnly = True

def _makeLastPage(comp, page):
	if len(comp.customPages) == 1 and comp.customPages[0] == page:
		return
	orderedpages = [p.name for p in comp.customPages if p != page] + [page.name]
	comp.sortCustomPages(*orderedpages)

def _addOrUpdatePar(appendmethod, name, label, value=None, expr=None, readonly=None, setdefault=False):
	p = appendmethod(name, label=label)[0]
	if expr is not None:
		p.expr = expr
		if setdefault:
			p.defaultExpr = expr
	elif value is not None:
		p.val = value
		if setdefault:
			p.default = value
	if readonly is not None:
		p.readOnly = readonly
	return p

def _addOrUpdateMetadataPar(appendmethod, name, label, value):
	_addOrUpdatePar(appendmethod, name, label, value, readonly=True, setdefault=True)

def _setComponentMetadata(
		comp,
		description=None,
		version=None,
		typeid=None,
		website=None,
		author=None,
		page=':meta'):
	page = comp.appendCustomPage(page)
	if page.startswith(':'):
		_makeLastPage(comp, page)
	if typeid:
		_addOrUpdateMetadataPar(page.appendStr, 'Comptypeid', ':Type ID', typeid)
	_addOrUpdateMetadataPar(page.appendStr, 'Compdescription', ':Description', description)
	_addOrUpdateMetadataPar(page.appendInt, 'Compversion', ':Version', version)
	_addOrUpdateMetadataPar(page.appendStr, 'Compwebsite', ':Website', website)
	_addOrUpdateMetadataPar(page.appendStr, 'Compauthor', ':Author', author)
	page.sort('Comptypeid', 'Compdescription', 'Compversion', 'Compwebsite', 'Compauthor')

_basicToolCommands = [
	Command.forAction(
		_copyPaths,
		label='copy path',
		help='copy paths of selected ops'),
	Command.forAction(
		_saveTox,
		label='save',
		help='save selected or active component tox file'),
	Command.forAction(
		_incrementComponentVersion,
		label='version++',
		help='increment the component version attribute on selected or active',
	),
]
