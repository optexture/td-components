from dataclasses import dataclass

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from typing import Any
	iop.workspaceState = COMP()
	ipar.workspaceState = Any()


@dataclass
class ToolContext:
	toolName: str
	component: 'COMP'
	editorPane: 'NetworkEditor'

class EditorTools(SettingsExtBase):
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def LoadCustomTools(self):
		pass

	def ExecuteTool(self, name):
		pass
