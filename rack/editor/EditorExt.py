from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from _stubs.PopDialogExt import PopDialogExt
	from .components.SettingsExt import UserSettings
	from .components.EditorViewsExt import EditorViews
	from .components.EditorToolsExt import EditorTools
	from ui.statusOverlayExt import StatusOverlay
	iop.hostedComp = COMP()
	ipar.editorState = Any()
	ipar.workspace = Any()
	ipar.compPicker = Any()
	ipar.editorUIState = Any()
	iop.libraryLoader = LibraryLoader(None)
	iop.userSettings = UserSettings(None)
	iop.editorViews = EditorViews(None)
	iop.editorTools = EditorTools(None)
	iop.statusOverlay = StatusOverlay(None)

try:
	from EditorCommon import *
except ImportError:
	from .components.EditorCommon import *

class Editor:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP
		self.loadComponentMessageId = None

	def hasExposedSubComponents(self):
		if not ipar.workspace.Exposesubcomps or not self.hasComponent():
			return False
		return self.ownerComp.op('sub_comp_table').numRows > 1

	@staticmethod
	def hasComponent():
		return ipar.editorState.Hascomponent.eval()

	@property
	def Workspace(self) -> 'Workspace':
		return iop.workspace

	@property
	def HostedComponent(self) -> 'COMP':
		return iop.hostedComp

	@property
	def StatusOverlay(self) -> 'StatusOverlay':
		return iop.statusOverlay

	def getLeftTabSet(self):
		return UITabSet(
			tabs=[
				UITab.noneTab(),
				UITab(
					name='component_picker',
					label='Component Picker',
					componentName='component_picker',
					icon=chr(0xF572),
					visible=bool(ipar.workspace.Rootfolder),
				),
				UITab(
					name='opBrowser',
					label='Sub-Components',
					componentName='opBrowser',
					visible=self.hasExposedSubComponents(),
					icon=chr(0xF645),
				)
			],
		)

	def getRightTabSet(self):
		return UITabSet(
			attrNames=[
				'paramsOp', 'paramsPage', 'paramsScope', 'paramsCombine',
				'showSubCompSelector',
			],
			tabs=[
				UITab.noneTab(),
				UITab(
					name='component_params',
					label='Component Parameters',
					componentName='parameters',
					icon=chr(0xFB5E),
					visible=self.hasComponent(),
					attrs={
						'paramsOp': iop.hostedComp,
						'paramsPage': '*',
						'paramsScope': '*',
						'paramsCombine': 'any',
						'showSubCompSelector': '0',
					}
				),
				UITab(
					name='sub_component_params',
					label='Sub-Component Parameters',
					componentName='parameters',
					icon=chr(0xFB5F),
					visible=self.hasExposedSubComponents(),
					attrs={
						'paramsOp': op(self.ownerComp.op('sub_comp_dropmenu').par.Value0),
						'paramsPage': '*',
						'paramsScope': '*',
						'paramsCombine': 'any',
						'showSubCompSelector': '1',
					}
				),
				UITab(
					name='recorder',
					label='Recorder Settings',
					componentName='parameters',
					icon=chr(0xF44A),
					visible=self.hasComponent(),
					attrs={
						'paramsOp': iop.recorder,
						'paramsPage': 'Output Format Advanced',
						'paramsScope': '',
						'paramsCombine': 'any',
						'showSubCompSelector': '0',
					}
				),
				UITab(
					name='workspace_settings',
					label='Workspace Settings',
					componentName='parameters',
					icon=chr(0xF493),
					visible=bool(ipar.workspace.Rootfolder),
					attrs={
						'paramsOp': iop.workspace,
						'paramsPage': 'Settings',
						'paramsScope': '^Settings',
						'paramsCombine': 'all',
						'showSubCompSelector': '0',
					}
				),
			],
		)

	def getBodyTabSet(self):
		tabs = UITabSet(
			tabs=[
				UITab(
					name='preview_panel',
					label='Preview',
					componentName='preview_panel',
					visible=self.hasComponent(),
				)
			],
		)
		# TODO: custom editor views
		return tabs

	def updateLeftPanelTabs(self):
		tabs = self.getLeftTabSet()
		tabs.buildTable(self.ownerComp.op('set_left_panel_tabs'))
		tabs.updateParMenu(ipar.editorUIState.Selectedleftpanel)

	def updateRightPanelTabs(self):
		tabs = self.getRightTabSet()
		tabs.buildTable(self.ownerComp.op('set_right_panel_tabs'))
		tabs.updateParMenu(ipar.editorUIState.Selectedrightpanel)

	def updateBodyPanelTabs(self):
		tabs = self.getBodyTabSet()
		tabs.buildTable(self.ownerComp.op('set_body_panel_tabs'))
		tabs.updateParMenu(ipar.editorUIState.Selectedview)

	def OnPickerItemSelect(self, compInfo: DAT):
		if compInfo.numRows < 2:
			self.LoadComponent(None)
		else:
			tox = compInfo[1, 'tox'].val
			thumb = compInfo[1, 'thumb'].val
			self.LoadComponent(tox, thumb)

	def queueMethodCall(self, method: str, *args):
		if '.' in method:
			run(method, *args, delayFrames=5, delayRef=root)
		else:
			run(f'args[0].{method}(*(args[1:]))', self, *args, delayFrames=5, delayRef=root)

	def showStatusMessage(self, message: str, static=False):
		print(self.ownerComp, 'STATUS', message)
		ui.status = message
		if static:
			return iop.statusOverlay.AddStaticMessage(message)
		else:
			iop.statusOverlay.AddMessage(message)

	@staticmethod
	def clearStatusMessage(messageId: int):
		if messageId is not None:
			iop.statusOverlay.ClearMessage(messageId)

	def LoadComponent(
			self,
			tox: Optional[str], thumb: Optional[str] = None,
			thenRun: str = None, runArgs: list = None):
		if not tox:
			self.loadComponentMessageId = self.showStatusMessage('Unloading component...')
			self.queueMethodCall('unloadComponent_stage', 0, thenRun, runArgs)
		else:
			self.loadComponentMessageId = self.showStatusMessage(f'Loading component {tox}...')
			self.queueMethodCall('loadComponent_stage', 0, tox, thumb, thenRun, runArgs)

	def loadComponent_stage(
			self,
			stage: int,
			tox: Optional[str], thumb: Optional[str] = None,
			thenRun: str = None, runArgs: list = None):
		print(self.ownerComp, 'loadComponent stage ', stage)
		comp = iop.hostedComp
		if stage == 0:
			self.showStatusMessage('Loading tox file')
			comp.allowCooking = False
			comp.par.externaltox = tox
			comp.par.reinitnet.pulse()
			self.queueMethodCall('loadComponent_stage', stage + 1, tox, thumb, thenRun, runArgs)
		elif stage == 1:
			self.updateComponentProperties(tox, thumb)
			self.queueMethodCall('loadComponent_stage', stage + 1, tox, thumb, thenRun, runArgs)
		elif stage == 2:
			self.updateComponentOutputs()
			self.queueMethodCall('loadComponent_stage', stage + 1, tox, thumb, thenRun, runArgs)
		elif stage == 3:
			self.updateUIAfterComponentLoad()
			self.queueMethodCall('loadComponent_stage', stage + 1, tox, thumb, thenRun, runArgs)
		elif stage == 4:
			self.showStatusMessage('Enabling cooking in component')
			comp.allowCooking = True
			if thenRun:
				self.queueMethodCall(thenRun, *(runArgs or []))
			self.clearStatusMessage(self.loadComponentMessageId)
			self.loadComponentMessageId = None

	def unloadComponent_stage(
			self, stage: int,
			thenRun: str = None, runArgs: list = None):
		print(self.ownerComp, 'unloadComponent stage ', stage)
		comp = iop.hostedComp
		if stage == 0:
			if comp.par.externaltox:
				self.showStatusMessage('Detaching tox')
				comp.par.externaltox = ''
				self.queueMethodCall('unloadComponent_stage', stage + 1, thenRun, runArgs)
			else:
				self.unloadComponent_stage(stage + 1, thenRun, runArgs)
		elif stage == 1:
			if comp.customPars:
				self.showStatusMessage('Destroying component parameters')
				comp.destroyCustomPars()
				self.queueMethodCall('unloadComponent_stage', stage + 1, thenRun, runArgs)
			else:
				self.unloadComponent_stage(stage + 1, thenRun, runArgs)
		elif stage == 2:
			if comp.children:
				self.showStatusMessage('Destroying child components')
				for child in list(comp.children):
					if child.valid:
						child.destroy()
				self.queueMethodCall('unloadComponent_stage', stage + 1, thenRun, runArgs)
			else:
				self.unloadComponent_stage(stage + 1, thenRun, runArgs)
		elif stage == 3:
			self.updateComponentProperties(None, None)
			self.queueMethodCall('unloadComponent_stage', stage + 1, thenRun, runArgs)
		elif stage == 4:
			self.updateComponentOutputs()
			self.queueMethodCall('unloadComponent_stage', stage + 1, thenRun, runArgs)
		elif stage == 5:
			self.updateUIAfterComponentLoad()
			self.queueMethodCall('unloadComponent_stage', stage + 1, thenRun, runArgs)
		elif stage == 6:
			if ipar.compPicker.Selectedcomp:
				self.showStatusMessage('Deselecting component in picker')
				ipar.compPicker.Selectedcomp = ''
			if thenRun:
				self.queueMethodCall(thenRun, *(runArgs or []))
			self.clearStatusMessage(self.loadComponentMessageId)
			self.loadComponentMessageId = None

	def updateUIAfterComponentLoad(self):
		self.showStatusMessage('Updating UI after component change')
		# self.ownerComp.op('body_panel_tabbar').par.Value0 = 'preview_panel'
		# self.ownerComp.op('sel_selected_body_panel_tab').cook(force=True)
		self.updateLeftPanelTabs()
		self.updateRightPanelTabs()
		self.updateBodyPanelTabs()
		self.ReloadMenu()

	def SaveComponent(self, tox: str = None, thumb: str = None):
		self.queueMethodCall('saveComponent_stage', 0, tox, thumb)

	def saveComponent_stage(self, stage: int, tox: str = None, thumb: str = None):
		print(self.ownerComp, 'saveComponent stage', stage)
		comp = iop.hostedComp
		if stage == 0:
			if tox:
				ipar.editorState.Toxfile.val = tox
				if thumb and ipar.workspace.Savethumbnail:
					ipar.editorState.Thumbfile.val = thumb
			else:
				tox = ipar.editorState.Toxfile.eval()
				if not tox:
					return
				if ipar.workspace.Savethumbnail:
					if thumb:
						ipar.editorState.Thumbfile.val = thumb
					else:
						thumb = ipar.editorState.Thumbfile.eval()
			self.queueMethodCall('saveComponent_stage', stage + 1, tox, thumb)
		elif stage == 1:
			expandedPath = Path(tdu.expandPath(tox))
			msg = f'Saving component to {expandedPath}'
			print(msg)
			ui.status = msg
			comp.save(tox, createFolders=True)
			self.queueMethodCall('saveComponent_stage', stage + 1, tox, thumb)
		elif stage == 2:
			self.updateComponentProperties(tox, thumb)
			self.queueMethodCall('saveComponent_stage', stage + 1, tox, thumb)
		elif stage == 3:
			if ipar.workspace.Savethumbnail:
				thumbSource = ipar.editorState.Videooutput.eval()  # type: TOP
				if thumbSource:
					if not thumb:
						expandedPath = Path(tdu.expandPath(tox))
						thumb = expandedPath.with_suffix('.png')
						ipar.editorState.Thumbfile = thumb
					thumbSource.save(thumb)

	def updateComponentProperties(self, tox: Optional[str], thumb: Optional[str]):
		self.showStatusMessage('Updating component properties')
		if not tox:
			ipar.editorState.Hascomponent = False
			ipar.editorState.Thumbfile = ''
			ipar.editorState.Toxfile = ''
			ipar.editorState.Name = ''
			ipar.editorState.Modifieddate = ''
			ipar.editorState.Hascomponentui = False
		else:
			toxPath = Path(tox)
			ipar.editorState.Name = toxPath.stem
			ipar.editorState.Thumbfile = thumb or ''
			ipar.editorState.Toxfile = tox
			modified = datetime.fromtimestamp(toxPath.stat().st_mtime)
			ipar.editorState.Modifieddate = modified.strftime('%Y-%m-%d %H:%M')
			ipar.editorState.Hascomponent = True
			ipar.editorState.Hascomponentui = iop.hostedComp.isPanel

	def UnloadComponent(self):
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
		showPromptDialog(
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
	def showNetwork(useActive=True):
		comp = iop.hostedComp
		pane = None
		if useActive:
			pane = getActiveEditor()
		if not pane:
			pane = getPaneByName('compeditor')
		if not pane:
			pane = ui.panes.createFloating(type=PaneType.NETWORKEDITOR, name='compeditor')
		pane.owner = comp

	@staticmethod
	def GetActiveNetworkEditor():
		return getActiveEditor()

	def ShowNetwork(self):
		self.showNetwork(useActive=True)

	def ShowNetworkPopup(self):
		self.showNetwork(useActive=False)

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

	def updateComponentOutputs(self):
		self.showStatusMessage('Locating component outputs')
		ipar.editorState.Videooutput = self.FindVideoOutput() or ''
		ipar.editorState.Audiooutput = self.FindAudioOutput() or ''

	@staticmethod
	def CustomizeComponent():
		comp = iop.hostedComp
		ui.openCOMPEditor(comp)

	def OnWorkspaceUnload(self):
		self.queueMethodCall('onWorkspaceUnload_stage', 0)

	def onWorkspaceUnload_stage(self, stage: int, thenRun: str = None, runArgs: list = None):
		print(self.ownerComp, 'onWorkspaceUnload stage', stage)
		if stage == 0:
			self.LoadComponent(None, None, 'onWorkspaceUnload_stage', [stage + 1, thenRun, runArgs])
		elif stage == 1:
			print(self.ownerComp, 'Refresh picker')
			ipar.compPicker.Refreshpulse.pulse()
			self.queueMethodCall('onWorkspaceUnload_stage', stage + 1, thenRun, runArgs)
		elif stage == 2:
			print(self.ownerComp, 'unload libraries')
			iop.libraryLoader.UnloadLibraries()
			self.queueMethodCall('onWorkspaceUnload_stage', stage + 1, thenRun, runArgs)
		elif stage == 3:
			print('reload menu')
			self.ReloadMenu()
			self.queueMethodCall('onWorkspaceUnload_stage', stage + 1, thenRun, runArgs)
		elif stage == 4:
			print(self.ownerComp, 'update editor views')
			iop.editorViews.OnWorkspaceUnload()
			self.queueMethodCall('onWorkspaceUnload_stage', stage + 1, thenRun, runArgs)
		elif stage == 5:
			print(self.ownerComp, 'update editor tools')
			iop.editorTools.OnWorkspaceUnload()
			if thenRun:
				self.queueMethodCall(thenRun, *(runArgs or []))

	def OnWorkspaceLoad(self):
		self.queueMethodCall('onWorkspaceLoad_stage', 0)

	def onWorkspaceLoad_stage(self, stage: int):
		print(self.ownerComp, 'onWorkspaceLoad_stage', stage)
		if stage == 0:
			self.onWorkspaceUnload_stage(0, 'onWorkspaceLoad_stage', [stage + 1])
		elif stage == 1:
			print(self.ownerComp, 'load libraries')
			iop.libraryLoader.LoadLibraries()
			self.queueMethodCall('onWorkspaceLoad_stage', stage + 1)
		elif stage == 2:
			print(self.ownerComp, 'add recent workspace')
			iop.userSettings.AddRecentWorkspace(ipar.workspace.Settingsfile.eval())
			self.queueMethodCall('onWorkspaceLoad_stage', stage + 1)
		elif stage == 3:
			print(self.ownerComp, 'reload menu')
			self.ReloadMenu()
			self.queueMethodCall('onWorkspaceLoad_stage', stage + 1)
		elif stage == 4:
			print(self.ownerComp, 'update editor views')
			iop.editorViews.OnWorkspaceLoad()
			self.queueMethodCall('onWorkspaceLoad_stage', stage + 1)
		elif stage == 5:
			print(self.ownerComp, 'load editor tools')
			iop.editorViews.OnWorkspaceLoad()

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
				itemValue = define.get('itemValue')
				if itemValue in (None, ''):
					run(f'args[0].{method}()', actionOp, delayFrames=2)
				else:
					run(f'args[0].{method}(args[1])', actionOp, itemValue, delayFrames=2)

	def GetMenuItems(self, rowDict: dict, **kwargs):
		# print(self.ownerComp, 'GetMenuItems', rowDict)
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

	def ReloadMenu(self):
		menu = self.ownerComp.op('topMenu')
		menu.allowCooking = False
		menu.allowCooking = True

def showPromptDialog(
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

def getActiveEditor():
	pane = ui.panes.current
	if pane.type == PaneType.NETWORKEDITOR:
		return pane
	for pane in ui.panes:
		if pane.type == PaneType.NETWORKEDITOR:
			return pane

def getPaneByName(name):
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
		libs = self.parseLibraries()
		if not libs:
			return
		dat.appendRows([list(dataclasses.astuple(lib)) for lib in libs])

	def parseLibraries(self):
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
			libs.append(LibrarySpec(shortcut, str(actualPath or ''), tox))
		return libs

	def LoadLibraries(self):
		libs = self.parseLibraries()
		for i, lib in enumerate(libs):
			if not lib.path:
				continue
			if lib.shortcut and hasattr(op, lib.shortcut):
				continue
			comp = self.ownerComp.loadTox(lib.path)
			comp.par.externaltox = lib.path
			if lib.shortcut:
				comp.par.opshortcut = lib.shortcut
			comp.nodeY = 600 - (i * 150)
