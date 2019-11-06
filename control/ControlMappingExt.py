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

class ControlMapper:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp

	@staticmethod
	def PrepareDevices(dat):
		dat.appendCols([['label'], ['sliders'], ['buttons']])
		for i in range(1, dat.numRows):
			indev = dat[i, 'indevice']
			outdev = dat[i, 'outdevice']
			if indev == outdev:
				dat[i, 'label'] = indev
			else:
				dat[i, 'label'] = '{} / {}'.format(indev, outdev)
			devDef = op(dat[i, 'definition'] or '')
			if devDef:
				dat[i, 'sliders'] = devDef.op('sliders') or ''
				dat[i, 'buttons'] = devDef.op('buttons') or ''
		# Ensure that the table has placeholders to fill up to 16 entries
		for i in range(dat.numRows, 17):
			dat.appendRow([i])
			name = '({})'.format(i)
			dat[i, 'indevice'] = name
			dat[i, 'outdevice'] = name
			dat[i, 'label'] = name + ' (unknown)'
			dat[i, 'channel'] = 1

	@staticmethod
	def BuildDeviceControls(outDat: 'DAT', deviceDat: 'DAT'):
		outDat.clear()
		outDat.appendRow([
			'control',
			'cc',
			'chan',
		])
		sliders = op(deviceDat[1, 'sliders'])  # type: DAT
		buttons = op(deviceDat[1, 'buttons'])  # type: DAT
		for ctrlTable in [sliders, buttons]:
			if not ctrlTable or ctrlTable.numCols < 2:
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
					cc = int(parts[1])
				except ValueError:
					cc = None
				if cc is None:
					continue
				outDat.appendRow([
					name,
					cc,
					'ch1c{}'.format(cc),
				])

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
				return
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
			param = mapDat[i, 'param'].val
			if not path or not param:
				continue
			if path in opPars:
				opPars[path].append(param)
			else:
				opPars[path] = [param]
		for path, params in opPars.items():
			outDat.appendRow([path] + params)

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
		outDat[row, 'group'] = inDat[inRow, 'group'].val + groups
		outDat[row, 'parType'] = 'pulse' if isPulse else 'value'
		outDat[row, 'control'] = control
		outDat[row, 'cc'] = cc
		outDat[row, 'chan'] = chan
