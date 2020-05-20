from typing import List, Union

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

class ControlTarget:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	def HandleActionPulse(self, action):
		if action == 'Initmaptable':
			self._InitTable(createMissing=True, clearExisting=False)
		elif action == 'Clearmaptable':
			self._InitTable(createMissing=False, clearExisting=True)
		elif action == 'Editmaptable':
			self._InitTable(createMissing=True, clearExisting=False)
			dat = self.ownerComp.par.Maptable.eval()
			if dat:
				dat.openViewer()

	def _InitTable(self, createMissing=False, clearExisting=False):
		par = self.ownerComp.par.Maptable
		dat = par.eval()  # type: DAT
		if not dat and createMissing:
			dat = self.ownerComp.parent().create(tableDAT, 'mappings')
			dat.nodeX = self.ownerComp.nodeX + self.ownerComp.nodeWidth + 50
			dat.nodeY = self.ownerComp.nodeY
			par.val = dat
		if not dat:
			return
		if clearExisting:
			dat.clear()
		if dat.numRows == 1 and dat.numCols == 1 and dat[0, 0] == '':
			dat.clear()
		mappingColumns = [
			'path',
			'param',
			'enable',
			'low',
			'high',
			'control',
			'group',
		]
		if not dat.numRows:
			dat.appendRow(mappingColumns)
		else:
			for col in mappingColumns:
				if not dat.col(col):
					dat.appendCol([col])

	def AddMappingForParam(self, par: 'Par', control: str = None, enable: bool = False):
		self._InitTable(createMissing=True, clearExisting=False)
		table = self.ownerComp.par.Maptable.eval()  # type: DAT
		root = self.ownerComp.par.Targetroot.eval()
		if par.owner == root:
			path = ''
		elif root:
			path = root.relativePath(par.owner)
		else:
			path = par.owner.path
		i = table.numRows
		table.appendRow([])
		table[i, 'path'] = path
		table[i, 'param'] = par.name
		table[i, 'enable'] = int(enable)
		table[i, 'control'] = control or ''

def BuildDeviceControls(outDat: 'DAT', definition: 'COMP'):
	outDat.clear()
	outDat.appendRow([
		'control',
		'cc',
		'chan',
	])
	if not definition:
		return
	for ctrlTable in definition.ops('sliders', 'buttons'):
		if not ctrlTable or not ctrlTable.valid or ctrlTable.numCols < 2:
			continue
		for ctrlRow in range(ctrlTable.numRows):
			name = ctrlTable[ctrlRow, 0]
			if not name:
				continue
			pattern = ctrlTable[ctrlRow, 1].val
			if not pattern:
				continue
			parts = pattern.split(' ')
			if len(parts) != 3:
				continue
			try:
				cc = int(parts[1], 16)
			except ValueError:
				cc = None
			if cc is None:
				continue
			outDat.appendRow([
				name,
				cc,
				'ch1c{}'.format(cc),
			])

class ControlMapper:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp
		self.statePar = ownerComp.op('iparMapperState').par

	@staticmethod
	def BuildDeviceControls(outDat: 'DAT', definition: 'COMP'):
		BuildDeviceControls(outDat, definition)

	@staticmethod
	def BuildMapTable(outDat: 'DAT', targets: List[str], deviceControls: 'DAT'):
		outDat.clear()
		outDat.appendRow([
			'param',
			'path',
			'parName',
			'enable',
			'low',
			'high',
			'targetName',
			'group',
			'parType',
			'control',
			'cc',
			'chan',
		])
		for target in ops(*targets):
			mappings = target.op('mappings')
			if not mappings or mappings.numRows < 2:
				continue
			_AddToMapTable(
				outDat,
				mappings,
				targetRoot=op(getattr(target.par, 'Targetroot', None)),
				targetName=str(getattr(target.par, 'Targetname', '')),
				groups=str(getattr(target.par, 'Group', '')),
				deviceControls=deviceControls,
			)

	@staticmethod
	def BuildOpPars(outDat: 'DAT', mapDat: 'DAT'):
		outDat.clear()
		opPars = {}
		for i in range(1, mapDat.numRows):
			path = mapDat[i, 'path'].val
			param = mapDat[i, 'parName'].val
			if not path or not param:
				continue
			if path in opPars:
				opPars[path].append(param)
			else:
				opPars[path] = [param]
		for path, params in opPars.items():
			outDat.appendRow([path] + params)

	def HandleDrop(self, dropName, dropExt, baseName, destPath):
		print(f'{self.ownerComp}.HandleDrop(dropName: {dropName}, dropExt: {dropExt}, baseName: {baseName}, destPath: {destPath}')
		if dropExt != 'parameter':
			return
		o = op(baseName)
		print(f'DROP O {o!r}')
		if not o:
			return
		par = getattr(o.par, dropName, None)
		print(f'DROP PAR {par!r}')
		if par is None:
			return
		target = self.statePar.Selectedtarget.eval()  # type: ControlTarget
		if not target:
			return
		target.AddMappingForParam(par)



def _AddToMapTable(
		outDat: 'DAT',
		inDat: 'DAT',
		targetRoot: Union[str, 'OP'],
		targetName: str,
		groups: str,
		deviceControls: 'DAT'):
	relOp = op(targetRoot)
	if relOp and not targetName:
		targetName = relOp.path
	if groups:
		groups = ' ' + groups
	if relOp and not targetName:
		targetName = relOp.path
	for inRow in range(1, inDat.numRows):
		enabled = inDat[inRow, 'enable'] in ('True', '1', '')
		if not enabled:
			continue
		control = inDat[inRow, 'control']
		if control and deviceControls.row(control):
			cc = deviceControls[control, 'cc']
			chan = deviceControls[control, 'chan']
		else:
			cc = ''
			chan = ''
		relPath = inDat[inRow, 'path']
		if not relPath:
			o = relOp
		else:
			o = relOp.op(relPath) if relOp else op(relOp)
		if not o:
			continue
		par = getattr(o.par, str(inDat[inRow, 'param']), None) if o else None
		if par is None:
			isPulse = False
			low = ''
			high = ''
			parName = ''
		else:
			if not (par.isNumber or par.isToggle or par.isMenu):
				continue
			parName = par.name
			isPulse = par.isPulse or par.isMomentary
			low = inDat[inRow, 'low'].val
			high = inDat[inRow, 'high'].val
			if isPulse:
				low = 0
				high = 1
			else:
				if low == '':
					if par.isMenu:
						low = 0
					else:
						low = par.normMin
				if high == '':
					if par.isMenu:
						high = len(par.menuNames) - 1
					else:
						high = par.normMax
		row = outDat.numRows
		outDat.appendRow([])
		outDat[row, 'param'] = o.path + ':' + parName
		outDat[row, 'path'] = o.path
		outDat[row, 'parName'] = parName
		outDat[row, 'enable'] = int(enabled)
		outDat[row, 'low'] = low
		outDat[row, 'high'] = high
		outDat[row, 'targetName'] = targetName
		outDat[row, 'group'] = (inDat[inRow, 'group'].val + groups).strip()
		outDat[row, 'parType'] = 'pulse' if isPulse else 'value'
		outDat[row, 'control'] = control
		outDat[row, 'cc'] = cc
		outDat[row, 'chan'] = chan

class DeviceDisplay:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	@staticmethod
	def BuildDeviceControls(outDat: 'DAT', definition: 'COMP'):
		BuildDeviceControls(outDat, definition)

	@staticmethod
	def BuildLayout(outDat: 'DAT', layout: 'DAT', mappings: 'DAT', controls: 'DAT'):
		outDat.clear()
		outDat.appendRow([
			'label',
			'page', 'row', 'col',
			'slider', 'button',
			'sliderChan', 'buttonChan',
			'mappingLabel', 'mappingHelp',
		])
		if not layout:
			return
		for i in range(1, layout.numRows):
			slider = _cellOrDefault(layout, i, 'slider', '')
			button = _cellOrDefault(layout, i, 'button', '')
			controlLabelParts = []
			mapLabel = ''
			mapHelp = ''
			if slider:
				controlLabelParts.append(slider)
				sliderParam = mappings[slider, 'param'] if mappings else None
				if sliderParam:
					mapLabel = _getParamLabel(sliderParam)
					mapHelp = sliderParam.val
			if button:
				controlLabelParts.append(button)
				buttonParam = mappings[button, 'param'] if mappings else None
				if buttonParam:
					if mapLabel:
						mapLabel = 's: {}'.format(mapLabel)
					mapLabel += '\\nb: ' + _getParamLabel(buttonParam)
					if mapHelp:
						mapHelp = 's: {}: '.format(mapHelp)
					mapHelp += '\\nb: ' + buttonParam.val

			outDat.appendRow([
				' | '.join(controlLabelParts),
				_cellOrDefault(layout, i, 'page', 0),
				_cellOrDefault(layout, i, 'row', 0),
				_cellOrDefault(layout, i, 'col', 0),
				slider,
				button,
				_cellOrDefault(controls, _cellOrDefault(layout, i, 'slider', None), 'chan', ''),
				_cellOrDefault(controls, _cellOrDefault(layout, i, 'button', None), 'chan', ''),
				mapLabel,
				mapHelp,
			])

	@staticmethod
	def BuildControlMappings(outDat: 'DAT', controls: 'DAT', mappings: 'DAT'):
		outDat.clear()
		outDat.appendRow(['control', 'param', 'paramLabel'])
		for control in controls.col('control')[1:]:
			if not mappings or not control or not mappings.row(control):
				param = None
			else:
				param = mappings[control, 'param']
			outDat.appendRow([
				control,
				param or '',
				'\\n'.join(param.val.split(':')) if param else '',
			])

	@staticmethod
	def BuildPages(outDat: 'DAT', definition: 'COMP', layout: 'DAT'):
		outDat.clear()
		outDat.appendRow(['page', 'label', 'triggerChan', 'triggerCc', 'triggerChanName'])
		pages = definition.op('pages') if definition else None
		pageNames = set()
		if pages:
			for i in range(1, pages.numRows):
				name = pages[i, 'page']
				if not name:
					continue
				pageNames.add(name.val)
				chan = _cellOrDefault(pages, i, 'triggerChan', '')
				cc = _cellOrDefault(pages, i, 'triggerCc', '')
				outDat.appendRow([
					name,
					_cellOrDefault(pages, i, 'label', name),
					chan,
					cc,
					'ch{}c{}'.format(chan, cc),
				])
		for i in range(1, layout.numRows):
			page = layout[i, 'page'].val
			if page not in pageNames:
				pageNames.add(page)
				outDat.appendRow([page, page, '', ''])

def _getParamLabel(param):
	if not param:
		return ''
	param = str(param)
	if ':' not in param:
		return param
	path, parName = param.rsplit(':', 1)
	o = op(path)
	par = getattr(o.par, parName, None) if o else None
	if par is None:
		return parName
	return par.label

def _cellOrDefault(dat: 'DAT', r, c, default):
	if None in (dat, r, c):
		return default
	cell = dat[r, c]
	return cell.val if cell not in (None, '') else default
