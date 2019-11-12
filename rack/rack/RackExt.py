from typing import Optional, Tuple

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class Rack:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	@property
	def RackTools(self): return self.ownerComp.op('rack_tools')

	@property
	def RackToolsPane(self) -> Optional['Pane']:
		tools = self.RackTools
		for pane in ui.panes:
			if pane.owner == tools and pane.type == PaneType.PANEL:
				return pane

	@property
	def RackToolsPaneSize(self) -> Tuple[int, int]:
		pane = self.RackToolsPane
		if not pane:
			return 0, 0
		w = pane.topRight.x - pane.bottomLeft.x
		h = pane.topRight.y - pane.bottomLeft.y
		return w, h
