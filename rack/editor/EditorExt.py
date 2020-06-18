from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _stubs.PopDialogExt import PopDialogExt
	iop.hostedComp = COMP()
	ipar.editorState = Any()
	ipar.workspace = Any()
	ipar.compPicker = Any()

class Editor:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	def OnPickerItemSelect(self, compInfo: DAT):
		if compInfo.numRows < 2:
			self.LoadComponent(None)
		else:
			tox = compInfo[1, 'tox'].val
			thumb = compInfo[1, 'thumb'].val
			self.LoadComponent(tox, thumb)

	def LoadComponent(self, tox: Optional[str], thumb: Optional[str] = None):
		comp = iop.hostedComp
		if not tox:
			ipar.editorState.Hascomponent = False
			ipar.editorState.Thumbfile = ''
			ipar.editorState.Toxfile = ''
			ipar.editorState.Name = ''
			ipar.editorState.Modifieddate = ''
			ipar.editorState.Hascomponentui = False
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
			comp.par.reinitnet.pulse()
			comp = iop.hostedComp  # in case the OP was replaced due to an OP type change
			toxPath = Path(tox)
			ipar.editorState.Name = toxPath.stem
			modified = datetime.fromtimestamp(toxPath.stat().st_mtime)
			ipar.editorState.Modifieddate = modified.strftime('%Y-%m-%d %H:%M')
			ipar.editorState.Hascomponent = True
			ipar.editorState.Hascomponentui = comp.isPanel
		# Ensure that the video and audio outputs are found and updated
		iop.editorState.cook(force=True)

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

	def UnloadComponent(self):
		ipar.compPicker.Selectedcomp = ''
		self.LoadComponent(None)

	def PromptComponentSaveAs(self):
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
			if expandedPath.exists():
				result = ui.messageBox(
					'Overwrite file?',
					f'File already exists: {expandedPath}?\nAre you sure you want to overwrite it?',
					buttons=['Ok', 'Cancel'])
				if result != 0:
					return
			self.SaveComponent(tox)
			if not ipar.compPicker.Refresh:
				ipar.compPicker.Refreshpulse.pulse()

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

	@staticmethod
	def FindVideoOutput():
		comp = iop.hostedComp
		o = comp.op('video_out') or comp.op('out1')
		if o and o.isTOP:
			return o
		for o in comp.findChildren(type=outTOP, depth=1):
			return o

	@staticmethod
	def FindAudioOutput():
		comp = iop.hostedComp
		for name in ['audio_out', 'out1', 'out2']:
			o = comp.op(name)
			if o and o.isCHOP:
				return o
		for o in comp.findChildren(type=outCHOP, depth=1):
			return o

	@staticmethod
	def CustomizeComponent():
		comp = iop.hostedComp
		ui.openCOMPEditor(comp)

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
