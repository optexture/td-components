# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def getNormVal(p: 'Par'):
	if p is None or p.isPulse or p.isMomentary or p.isOP:
		return 0
	if p.isMenu:
		return p.menuIndex / (len(p.menuNames) - 1)
	if p.isString:
		return 0
	if p.isNumber:
		return p.normVal
	return 0

def setNormVal(p: 'Par', normVal: float):
	if p is None or p.isOP:
		return False
	if p.isPulse or p.isMomentary:
		p.pulse(1)
	elif p.isMenu:
		p.menuIndex = round(normVal * (len(p.menuNames) - 1))
	elif p.isString:
		return False
	elif p.isNumber:
		p.normVal = normVal
	else:
		return False
	return True

lastControl = None

def onMidiInput(channel: 'Channel'):
	p = ui.rolloverPar
	if p is None:
		return
	name = channel.name
	d = tdu.digits(name)
	if d is not None:
		name = tdu.base(name) + str(d - 1)
	op('set_output_val').par.name0 = name
	setNormVal(p, float(channel))
	pass

def onTableChange(dat):
	path = dat['path', 1].val
	o = path and op(path)
	if not o:
		return
	p = o.par[dat['param', 1]]
	normVal = 0
	if p is None:
		return
	if p.isPulse or p.isMomentary:
		return
	if p.isMenu:
		normVal = p.menuIndex / (len(p.menuNames)-1)
	elif p.isString:
		return
	elif p.isNumber:
		normVal = p.normVal
	op('set_output_val').par.value0 = normVal
	return

def onValueChange(channel, sampleIndex, val, prev):
	p = ui.rolloverPar
	# op('set_last_input_name')[0,0] = channel.name
	name = channel.name
	d = tdu.digits(name)
	if d is not None:
		name = tdu.base(name) + str(d - 1)
	op('set_output_val').par.name0 = name
	if p is None or p.isOP or p.isPython:
		return
	if p.isPulse or p.isMomentary:
		p.pulse()
	else:
		val /= 127.0
		if p.isMenu:
			i = round(val * (len(p.menuNames) - 1))
			p.menuIndex = i
		elif p.isString:
			return
		elif p.isNumber:
			if p.isInt:
				p.val = round(tdu.remap(val, 0, 1, p.normMin, p.normMax))
			else:
				p.normVal = val

class ParamAdjuster:
	def __init__(self, ownerComp: 'COMP'):
		self.ownerComp = ownerComp
		self.lastControl = None

	def onMidiInput(self, channel: 'Channel'):
		p = ui.rolloverPar
		if p is None:
			return
		if setNormVal(p, float(channel)):
			self.lastControl = tdu.digits(channel.name)

	def onRolloverParamChange(self):
		p = ui.rolloverPar
		pass
