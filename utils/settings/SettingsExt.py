import json

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *
	from typing import Any
	iop.hostedComp = COMP()
	ipar.compEditor = Any()
	from _stubs.TDCallbacksExt import CallbacksExt
	ext.Callbacks = CallbacksExt(None)

class Settings:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP

	@staticmethod
	def BuildSettings(parameters: 'DAT'):
		settings = {}
		for i in range(1, parameters.numRows):
			if parameters[i, 'readonly'] == '1' or parameters[i, 'enabled'] == '0':
				continue
			path = parameters[i, 'path'].val
			if path not in settings:
				settings[path] = {}
			name = parameters[i, 'name'].val
			mode = parameters[i, 'mode']
			if mode == '':
				settings[path][name] = parameters[i, 'value'].val
			elif mode == 'expression':
				settings[path][name] = {'$': parameters[i, 'expression'].val}
			elif mode == 'constant':
				settings[path][name] = parameters[i, 'constant'].val
		return settings

	def ParseSettings(self, settings: dict):
		if not settings:
			return
		for path, opSettings in settings.items():
			if not opSettings:
				continue
			o = op(path)
			if not o:
				continue
			for name, val in opSettings.items():
				par = o.par[name]  # type: Par
				if par is None:
					print(f'{self.ownerComp.path}: Warning par not found. path: {path} name: {name}')
					continue
				if isinstance(val, dict):
					if '$' not in val:
						print(f'{self.ownerComp.path}: Warning invalid setting. path: {path} name: {name} val: {val!r}')
						continue
					par.expr = val['$']
				else:
					if par.isNumber:
						par.val = float(val)
					elif par.isToggle:
						par.val = val in ['1', 'true', 1, True]
					else:
						par.val = val

	def OnFileInChange(self, dat: 'DAT'):
		if dat.text:
			settings = json.loads(dat.text)
		else:
			settings = {}
		self.ParseSettings(settings)

	def Save(self, par):
		file = self.ownerComp.par.File.eval()
		if not file:
			raise Exception('No settings file specified')
		self.ownerComp.op('fileout').par.write.pulse()

	def Load(self, par):
		fileIn = self.ownerComp.op('filein')
		if not fileIn.par.file:
			return
		fileIn.par.refreshpulse.pulse()
		if not self.ownerComp.par.Autoload:
			self.OnFileInChange(fileIn)

	def Autoload(self, par):
		if par:
			self.Load(par)

	def Autosave(self, par):
		if par:
			self.Save(par)
