from typing import List, Optional
from .EditorCommon import ComponentSpec

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class EditorViews:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP
		self.customHolder = ownerComp.op('customViews')  # type: COMP

	def LoadCustomViews(self):
		self.ClearCustomViews()
		viewDicts = self.ownerComp.par.Customviews.eval()
		if not viewDicts:
			return
		viewSpecs = [ComponentSpec.fromDict(v) for v in viewDicts]
		for i, viewSpec in enumerate(viewSpecs):
			comp = viewSpec.createComp(self.customHolder)
			comp.nodeY = 600 - (i * 150)
			self.initializeCustomView(comp, viewSpec)
		self.updateCustomViewTable(viewSpecs)

	def initializeCustomView(self, comp: 'COMP', viewSpec: ComponentSpec):
		if not comp.isPanel:
			return
		try:
			comp.par.hmode = 'fill'
			comp.par.vmode = 'fill'
			comp.par.display.expr = f'parent.editorViews.par.Selectedview == {viewSpec.name!r}'
		except Exception as e:
			print(self.ownerComp, 'Error initializing custom view', comp, '\n', viewSpec, '\n', e)

	def ClearCustomViews(self):
		for o in self.customHolder.children:
			if not o or not o.valid:
				continue
			try:
				o.destroy()
			except:
				pass
		self.updateCustomViewTable([])

	def OnWorkspaceUnload(self):
		self.ownerComp.par.Customviews = None
		self.ClearCustomViews()

	def OnWorkspaceLoad(self):
		self.LoadCustomViews()

	def updateCustomViewTable(self, viewSpecs: List[ComponentSpec]):
		dat = self.ownerComp.op('set_custom_view_table')
		dat.clear()
		dat.appendRow(['name', 'label'])
		if not viewSpecs:
			return
		for viewSpec in viewSpecs:
			dat.appendRow([viewSpec.name, viewSpec.label or viewSpec.name])
