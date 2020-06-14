from pathlib import Path
from typing import Any, Callable

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _stubs.PopDialogExt import PopDialogExt
	iop.hostedComp = COMP()
	ipar.editorState = Any()
	ipar.workspace = Any()

class Editor:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	def LoadComponent(self, tox: str, thumb: str = None):
		comp = iop.hostedComp
		if not tox:
			ipar.editorState.Thumbfile = ''
			ipar.editorState.Toxfile = ''
			comp.par.externaltox = ''
			comp.destroyCustomPars()
			for child in list(comp.children):
				if child.valid:
					try:
						child.destroy()
					except:
						pass
		else:
			msg = f'Loading component {tdu.expandPath(tox)}'
			print(msg)
			ui.status = msg
			ipar.editorState.Thumbfile = thumb or ''
			ipar.editorState.Toxfile = tox
			comp.par.externaltox = tox
			comp.par.reiinitnet.pulse()

	def SaveComponent(self, tox: str = None, thumb: str = None):
		comp = iop.hostedComp
		if tox:
			ipar.editorState.Toxfile.val = tox
			if thumb:
				ipar.editorState.Thumbfile.val = thumb
		else:
			tox = ipar.editorState.Toxfile.eval()
			if not tox:
				return
			if thumb:
				ipar.editorState.Thumbfile.val = thumb
			else:
				thumb = ipar.editorState.Thumbfile.eval()
		expandedPath = Path(tdu.expandPath(tox))
		msg = f'Saving component to {expandedPath}'
		print(msg)
		ui.status = msg
		comp.save(tox, createFolders=True)
		thumbSource = ipar.editorState.Videooutput.eval()  # type: TOP
		if thumbSource:
			if not thumb:
				thumb = expandedPath.with_suffix('.png')
				ipar.editorState.Thumbfile = thumb
			thumbSource.save(thumb)

	def PromptSaveAs(self):
		def _onOk(newName=None):
			if not newName:
				return
			rootFolder = Path(ipar.workspace.Rootfolder.eval())
			if not rootFolder:
				raise Exception('No workspace root folder!')
			layout = ipar.workspace.Folderlayout.eval()
			if layout == 'subirs':
				tox = rootFolder / newName / f'{newName}.tox'
			# elif layout == 'flat':
			else:
				tox = rootFolder / f'{newName}.tox'
			expandedPath = Path(tdu.expandPath(tox))
			if not expandedPath.exists():
				self.SaveComponent(tox)
			else:
				result = ui.messageBox(
					'Overwrite file?',
					f'File already exists: {expandedPath}?\nAre you sure you want to overwrite it?',
					buttons=['Ok', 'Cancel'])
				if result == 0:
					self.SaveComponent(tox)

		currentTox = ipar.editorState.Toxfile.eval()
		currentName = Path(currentTox).stem if currentTox else ''
		_ShowPromptDialog(
			title='Save component as',
			text='Choose component name',
			default=currentName,
			textentry=True,
			oktext='Save',
			ok=_onOk,
		)

	@staticmethod
	def ShowNetwork(useActive=True):
		comp = iop.hostedComp
		pane = None
		if useActive:
			pane = _GetActiveEditor()
		if not pane:
			pane = _GetPaneByName('compeditor')
		if not pane:
			pane = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name='compeditor')
		pane.owner = comp

def _ShowPromptDialog(
		title=None,
		text=None,
		default='',
		textentry=True,
		oktext='OK',
		canceltext='Cancel',
		ok: Callable = None,
		cancel: Callable = None):
	def _callback(info):
		if info['buttonNum'] == 1:
			if ok:
				if not text:
					ok()
				else:
					ok(info.get('enteredText'))
		elif info['buttonNum'] == 2:
			if cancel:
				cancel()
	dialog = op.TDResources.op('popDialog')  # type: PopDialogExt
	dialog.Open(
		title=title,
		text=text,
		textEntry=False if not textentry else (default or ''),
		buttons=[oktext, canceltext],
		enterButton=1, escButton=2, escOnClickAway=True,
		callback=_callback)

def _GetActiveEditor():
	pane = ui.panes.current
	if pane.type == PaneType.NETWORKEDITOR:
		return pane
	for pane in ui.panes:
		if pane.type == PaneType.NETWORKEDITOR:
			return pane

def _GetPaneByName(name):
	for pane in ui.panes:
		if pane.name == name:
			return pane
