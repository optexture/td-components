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

from common import ExtensionBase, loggedmethod, formatValue, parseValue

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
			name = parameters[i, 'name'].val
			mode = parameters[i, 'mode']
			key = f'{path}:{name}'
			if mode == '':
				settings[key] = parameters[i, 'value'].val
			elif mode == 'expression':
				settings[key] = {'$': parameters[i, 'expression'].val}
			elif mode == 'constant':
				settings[key] = parameters[i, 'constant'].val
		return settings
