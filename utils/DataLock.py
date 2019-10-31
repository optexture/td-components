def update(scriptOp):
	scriptOp.copy(scriptOp.inputs[0])

def onCook(scriptOp):
	if not parent().par.Locked:
		update(scriptOp)

def onPulse(par):
	scriptOp = op('data_lock')
	if par.name == 'Update':
		update(scriptOp)
	elif par.name == 'Clear':
		scriptOp.clear()

onStart = update
onCreate = update
