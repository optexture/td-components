import re

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from typing import Any
	iop.hostedComp = COMP()
	ipar.compEditor = Any()

class ComponentEditor:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	def LoadComponent(self):
		comp = iop.hostedComp
		tox = ipar.compEditor.Toxfile.eval()
		if not tox:
			comp.par.externaltox = ''
			comp.destroyCustomPars()
			for child in list(comp.children):
				if child.valid:
					child.destroy()
		else:
			msg = f'Loading component {tdu.expandPath(tox)}'
			print(msg)
			ui.status = msg
			# comp = comp.loadTox(tox, unwired=True)
			comp.par.externaltox = tox
			comp.par.reinitnet.pulse()
			comp = iop.hostedComp
			if comp.isPanel:
				panel = self.ownerComp.op('component_ui_panel')  # type: PanelCOMP
				if comp not in panel.panelChildren:
					panel.outputCOMPConnectors[0].connect(comp)

	def SaveComponent(self):
		comp = iop.hostedComp
		tox = ipar.compEditor.Toxfile.eval()
		if not tox:
			# TODO: prompt for a file
			ui.status = 'WARNING: UNABLE TO SAVE COMPONENT, NO TOX FILE'
			return
		tox = tdu.expandPath(tox)
		comp.save(tox, createFolders=False)
		msg = f'Saved component to {tox}'
		print(msg)
		ui.status = msg
		img = ipar.compEditor.Thumbfile.eval()
		if not img:
			img = re.sub(r'\.tox$', '.png', tox)
		self.ownerComp.op('video_output').save(img)

	@staticmethod
	def CustomizeComponent():
		comp = iop.hostedComp
		ui.openCOMPEditor(comp)

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

	def Savecomponent(self, par):
		self.SaveComponent()

	def Loadcomponent(self, par):
		self.LoadComponent()

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

def FindVideoOutput():
	comp = iop.hostedComp
	o = comp.op('video_out') or comp.op('out1')
	if o and o.isTOP:
		return o
	for o in comp.findChildren(type=outTOP, depth=1):
		return o
