from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
import dataclasses

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _stubs.PopDialogExt import PopDialogExt
	from .components.SettingsExt import UserSettings
	iop.hostedComp = COMP()
	ipar.editorState = Any()
	ipar.workspace = Any()
	ipar.compPicker = Any()
	ipar.editorUIState = Any()
	iop.libraryLoader = LibraryLoader(None)
	iop.userSettings = UserSettings(None)

class Editor:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP

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
		self.ownerComp.op('body_panel_tabbar').par.Value0 = 'preview_panel'
		self.ownerComp.op('sel_selected_body_panel_tab').cook(force=True)

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

	def saveComponentAs(self, newName: str):
		rootFolder = Path(ipar.workspace.Rootfolder.eval())
		if not rootFolder:
			raise Exception('No workspace root folder!')
		layout = ipar.workspace.Folderlayout.eval()
		if layout == 'subdirs':
			tox = rootFolder / newName / f'{newName}.tox'
		# elif layout == 'flat':
		else:
			tox = rootFolder / f'{newName}.tox'
		expandedPath = Path(tdu.expandPath(str(tox)))
		if expandedPath.exists():
			result = ui.messageBox(
				'Overwrite file?',
				f'File already exists: {expandedPath}?\nAre you sure you want to overwrite it?',
				buttons=['Ok', 'Cancel'])
			if result != 0:
				return
		self.SaveComponent(str(tox))
		if not ipar.compPicker.Refresh:
			ipar.compPicker.Refreshpulse.pulse()

	def PromptComponentSaveAs(self):
		def _onOk(newName=None):
			if not newName:
				return
			self.saveComponentAs(newName)

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

	def SaveComponentNewVersion(self):
		currentName = ipar.editorState.Name.eval()
		if not currentName:
			# TODO: error message?
			return
		baseName = tdu.base(currentName)
		version = tdu.digits(currentName) or 0
		newName = f'{baseName}{version + 1}'
		self.saveComponentAs(newName)

	@staticmethod
	def _ShowNetwork(useActive=True):
		comp = iop.hostedComp
		pane = None
		if useActive:
			pane = _GetActiveEditor()
		if not pane:
			pane = _GetPaneByName('compeditor')
		if not pane:
			pane = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name='compeditor')
		pane.owner = comp

	def ShowNetwork(self):
		self._ShowNetwork(useActive=True)

	def ShowNetworkPopup(self):
		self._ShowNetwork(useActive=False)

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

	def OnWorkspaceUnload(self):
		self.UnloadComponent()
		ipar.compPicker.Refreshpulse.pulse()
		iop.libraryLoader.UnloadLibraries()

	def OnWorkspaceLoad(self):
		self.OnWorkspaceUnload()
		iop.libraryLoader.LoadLibraries()
		iop.userSettings.AddRecentWorkspace(ipar.workspace.Settingsfile.eval())

	def OnMenuTrigger(self, define: dict = None, **kwargs):
		print(self.ownerComp, 'OnMenuTrigger', locals())
		if not define:
			return
		if 'statePar' in define:
			par = getattr(ipar.editorUIState, define['statePar'], None)
			if par is not None:
				if 'itemValue' in define:
					par.val = define['itemValue']
					return
				if par.isToggle:
					par.val = not par
					return
		actionOpName = define.get('actionOp')
		actionOp = getattr(iop, actionOpName, None) if actionOpName else self
		if actionOp is not None:
			method = define.get('actionMethod')
			if method and hasattr(actionOp, method):
				func = getattr(actionOp, method)
				itemValue = define.get('itemValue')
				if itemValue in (None, ''):
					func()
				else:
					func(itemValue)

	def GetMenuItems(self, rowDict: dict, **kwargs):
		print(self.ownerComp, 'GetMenuItems', rowDict)
		depth = rowDict.get('itemDepth', '')
		if depth == '':
			depth = 1
		nameKey = f'item{depth}'
		statePar = None  # type: Optional[Par]
		if rowDict.get('statePar'):
			statePar = getattr(ipar.editorUIState, rowDict['statePar'])
		if statePar is not None:
			if statePar.isMenu:
				optionCount = len(statePar.menuNames)
				return [
					{
						nameKey: label,
						'checked': f'ipar.editorUIState.{statePar.name} == {name!r}',
						'statePar': statePar.name,
						'itemValue': name,
						'callback': 'onItemTrigger',
						'dividerAfter': i == (optionCount - 1),
					}
					for i, (name, label) in enumerate(zip(statePar.menuNames, statePar.menuLabels))
				]
			elif statePar.isToggle:
				return {
					nameKey: statePar.label,
					'checked': f'ipar.editorUIState.{statePar.name}',
					'callback': 'onItemTrigger',
				}
		specialId = rowDict.get('specialId')
		if specialId == 'recentWorkspaces':
			workspaces = iop.userSettings.RecentWorkspaces()
			return [
				{
					nameKey: workspace,
					'checked': f'ipar.workspace.Settingsfile == {workspace!r}',
					'itemValue': workspace,
					'callback': 'onItemTrigger',
					'specialId': 'loadWorkspace',
					'dividerAfter': i == (len(workspaces) - 1),
					'actionOp': 'workspace',
					'actionMethod': 'LoadWorkspaceFile',
				}
				for i, workspace in enumerate(workspaces)
			]
		return []

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

class LibraryLoader:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP

	def UnloadLibraries(self):
		for o in self.ownerComp.children:
			if not o.valid or not o.isCOMP:
				continue
			try:
				o.destroy()
				pass
			except:
				pass

	# currently this is just for debugging purposes
	def BuildLibraryTable(self, dat: 'DAT'):
		dat.clear()
		dat.appendRow(['shortcut', 'path', 'allPaths'])
		libs = self._ParseLibraries()
		if not libs:
			return
		dat.appendRows([list(lib) for lib in libs])

	def _ParseLibraries(self):
		toxes = self.ownerComp.par.Libraries.eval() or []  # type: List[str]
		if not toxes:
			return []
		workspaceFolder = ipar.workspace.Rootfolder.eval()
		workspacePath = Path(workspaceFolder) if workspaceFolder else None
		libs = []
		for tox in toxes:
			if '@' in tox:
				shortcut, tox = tox.split('@')
			else:
				shortcut = ''
			actualPath = None
			for toxPath in tox.split('|'):
				if workspacePath and ':' not in toxPath and not toxPath.startswith('/'):
					effectivePath = workspacePath.joinpath(toxPath)
				else:
					effectivePath = Path(tdu.expandPath(toxPath))
				if effectivePath.exists():
					actualPath = effectivePath.resolve()
					break
			libs.append(_LibrarySpec(shortcut, str(actualPath or ''), tox))
		return libs

	def LoadLibraries(self):
		libs = self._ParseLibraries()
		for i, lib in enumerate(libs):
			if not lib.path:
				continue
			comp = self.ownerComp.loadTox(lib.path)
			comp.par.externaltox = lib.path
			if lib.shortcut:
				comp.par.opshortcut = lib.shortcut
			comp.nodeY = 600 - (i * 150)

@dataclass
class _LibrarySpec:
	shortcut: str
	path: str
	allPaths: str

@dataclass
class _ComponentSpec:
	tox: Optional[str] = None
	pars: Optional[Dict[str, Any]] = None

	@classmethod
	def fromDict(cls, d: dict):
		return cls(**d)

	def toDict(self):
		return dataclasses.asdict(self)
