# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from typing import Any
	iop.hostedComp = COMP()
	ipar.compEditor = Any()

def LoadComponent():
	comp = iop.hostedComp
	tox = ipar.compEditor.Toxfile.eval()
	if not tox:
		comp.par.externaltox = ''
		comp.destroyCustomPars()
		for child in comp.children:
			child.destroy()
	else:
		msg = f'Loading component {tox}'
		print(msg)
		ui.status = msg
		comp = comp.loadTox(tox, unwired=True)
		if comp.isPanel:
			panel = op('component_ui_panel')  # type: PanelCOMP
			if comp not in panel.panelChildren:
				panel.outputCOMPConnectors[0].connect(comp)

def FindVideoOutput():
	comp = iop.hostedComp
	o = comp.op('video_out') or comp.op('out1')
	if o and o.isTOP:
		return o
	for o in comp.findChildren(type=outTOP, depth=1):
		return o
