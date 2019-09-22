import typing as T

print('midimap.py loading...')

if False:
	from _stubs import *

class MidiMapper:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.mappings = []  # type: T.List[Mapping]
		self.LoadMapTable()

	@property
	def _ExternalMapTable(self):
		return self.ownerComp.par.Maptable.eval()

	@property
	def _InnerMapTable(self):
		return self.ownerComp.op('set_map_table')

	def LoadMapTable(self):
		self.mappings.clear()
		dat = self._ExternalMapTable
		if dat and dat.numRows:
			for i in range(1, dat.numRows):
				m = Mapping()
				m.ReadRow(dat, i)
				self.mappings.append(m)
		self._WriteMapTable(self._InnerMapTable)
		self._BuildActiveMappingTables()

	def SaveMapTable(self):
		dat = self._ExternalMapTable
		if not dat:
			raise Exception('No map table to write to!')
		self._WriteMapTable(dat)

	def _WriteMapTable(self, dat):
		dat.clear()
		dat.appendRow(Mapping.colnames)
		for m in self.mappings:
			m.WriteRow(dat)

	def _BuildActiveMappingTables(self):
		dat = self.ownerComp.op('set_active_mappings')
		dat.clear()
		dat.appendRow(['param', 'inchan', 'outchan', 'low', 'high', 'path', 'parname'])
		mappingsbyop = {}  # type: T.Dict[str, T.List[Mapping]]
		for m in self.mappings:
			if not m.enable or not m.path or not m.param or m.cc in ('', None):
				continue
			o = op(m.path)
			if not o:
				continue
			p = getattr(o.par, m.param, None)
			if p is None:
				continue
			if not (p.isNumber or p.isToggle or p.isMenu):
				continue
			dat.appendRow([
				'{}:{}'.format(o.path, m.param),
				'cc{}'.format(m.cc),
				'ch1c{}'.format(m.cc),
				_format(m.rangelow if m.rangelow is not None else p.normMin),
				_format(m.rangehigh if m.rangehigh is not None else p.normMax),
				o.path,
				m.param,
			])
			if o.path not in mappingsbyop:
				mappingsbyop[o.path] = []
			mappingsbyop[o.path].append(m)
		opsdat = self.ownerComp.op('set_mapped_ops')
		opsdat.clear()
		opsdat.appendRow(['path', 'params', 'fullparams', 'inchans', 'outchans'])
		for path in sorted(mappingsbyop.keys()):
			omaps = mappingsbyop[path]
			opsdat.appendRow([
				path,
				' '.join([m.param for m in omaps]),
				' '.join(['{}:{}'.format(path, m.param) for m in omaps]),
				' '.join(['cc{}'.format(m.cc) for m in omaps]),
				' '.join(['ch1c{}'.format(m.cc) for m in omaps]),
			])

	def HandleDrop(self, args):
		pass

	def _HandleDrop(self, args):
		pass

	@staticmethod
	def PrepareDevices(dat):
		dat.appendCol(['label'])
		for i in range(1, dat.numRows):
			indev = dat[i, 'indevice']
			outdev = dat[i, 'outdevice']
			if indev == outdev:
				dat[i, 'label'] = indev
			else:
				dat[i, 'label'] = '{} / {}'.format(indev, outdev)
		for i in range(dat.numRows, 17):
			dat.appendRow([i])
			name = '({})'.format(i)
			dat[i, 'indevice'] = name
			dat[i, 'outdevice'] = name
			dat[i, 'label'] = name + ' (unknown)'
			dat[i, 'channel'] = 1

class Mapping:
	def __init__(
			self,
			path=None,
			param=None,
			enable=True,
			rangelow=None,
			rangehigh=None,
			cc=None):
		self.path = path
		self.param = param
		self.enable = enable
		self.rangelow = rangelow
		self.rangehigh = rangehigh
		self.cc = cc

	colnames = ['path', 'param', 'enable', 'low', 'high', 'cc']

	def ReadRow(self, dat, i):
		self.path = _parse(dat[i, 'path'], str)
		self.param = _parse(dat[i, 'param'], str)
		self.enable = _parse(dat[i, 'enable'], bool, False)
		self.rangelow = _parse(dat[i, 'low'], float)
		self.rangehigh = _parse(dat[i, 'high'], float)
		self.cc = _parse(dat[i, 'cc'], int)

	def WriteRow(self, dat):
		i = dat.numRows
		dat.appendRow([])
		for c in Mapping.colnames:
			if dat.col(c) is None:
				dat.appendCol([c])
		dat[i, 'path'] = _format(self.path)
		dat[i, 'param'] = _format(self.param)
		dat[i, 'enable'] = _format(self.enable)
		dat[i, 'low'] = _format(self.rangelow)
		dat[i, 'high'] = _format(self.rangehigh)
		dat[i, 'cc'] = _format(self.cc)

def _parse(val, t, default=None):
	if val in ('', None):
		return default
	try:
		return t(val)
	except ValueError:
		return default

def _format(val):
	if val is None:
		return ''
	if isinstance(val, bool):
		return int(val)
	if isinstance(val, (int, float)):
		if val == int(val):
			return int(val)
	return val
