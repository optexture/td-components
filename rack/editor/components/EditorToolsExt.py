from dataclasses import dataclass, is_dataclass, asdict
from typing import Callable, List, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from ..EditorExt import Editor
	ext.editor = Editor(None)
	iop.hostedComp = COMP()

@dataclass
class ToolContext:
	toolName: str
	component: 'COMP'
	editorPane: 'NetworkEditor'

@dataclass
class _ToolDefinition:
	name: str
	action: Callable[[ToolContext], None]
	label: str = None
	icon: str = None

	@classmethod
	def parse(cls, spec: Union['_ToolDefinition', list, tuple, dict]) -> '_ToolDefinition':
		if isinstance(spec, _ToolDefinition):
			return spec
		if is_dataclass(spec):
			spec = asdict(spec)
		if isinstance(spec, dict):
			return cls(**spec)
		return cls(*spec)

class EditorTools:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp
		self.builtInTools = []  # type: List[_ToolDefinition]
		self.customTools = []  # type: List[_ToolDefinition]

		self.customToolsScript = self.ownerComp.op('customTools')  # type: DAT
		self.toolTable = self.ownerComp.op('set_tool_table')  # type: DAT

		self.initializeBuiltInTools()
		self.updateToolTable()

	def initializeBuiltInTools(self):
		self.builtInTools = [
			_ToolDefinition('saveComponent', lambda ctx: ext.editor.SaveComponent(), icon=chr(0xF193))
		]

	def updateToolTable(self):
		self.toolTable.clear()
		self.toolTable.appendRow(['name', 'label', 'icon', 'category'])
		for tool in self.builtInTools:
			self.toolTable.appendRow([
				tool.name,
				tool.label or tool.name,
				tool.icon or '',
				'builtIn'
			])
		for tool in self.customTools:
			self.toolTable.appendRow([
				tool.name,
				tool.label or tool.name,
				tool.icon or '',
				'custom'
			])

	def ClearCustomTools(self):
		self.customToolsScript.clear()
		self.ownerComp.par.Customtoolscriptfile = ''
		self.updateToolTable()

	def LoadCustomTools(self):
		self.customTools.clear()
		self.customToolsScript.clear()
		file = self.ownerComp.par.Customtoolscriptfile.eval()
		if not file:
			return
		self.customToolsScript.par.file = file
		self.customToolsScript.par.loadonstartpulse.pulse()
		if not self.customToolsScript.text:
			return
		m = self.customToolsScript.module
		if not hasattr(m, 'getEditorTools'):
			raise Exception('Custom tools script does not have `getEditorTools` function')
		specs = m.getEditorTools()
		if not specs:
			return
		for spec in specs:
			try:
				tool = _ToolDefinition.parse(spec)
			except Exception as e:
				print(self.ownerComp, f'ERROR parsing custom tool spec: {spec!r}\n{e}')
				continue
			self.customTools.append(tool)
		self.updateToolTable()

	def findTool(self, name: str):
		# custom tools take precedence over built-in tools
		for tool in self.customTools:
			if tool.name == name:
				return tool
		for tool in self.builtInTools:
			if tool.name == name:
				return tool

	def ExecuteTool(self, name: str):
		tool = self.findTool(name)
		if not tool:
			raise Exception(f'Editor tool not found: {name}')
		context = ToolContext(
			name,
			iop.hostedComp,
			ext.editor.GetActiveNetworkEditor())
		tool.action(context)

	def OnWorkspaceLoad(self):
		self.LoadCustomTools()

	def OnWorkspaceUnload(self):
		self.ClearCustomTools()
