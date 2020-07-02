# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

def InitHost():
	filterOp = parent()
	hostOp = filterOp.par.Parfilterop.eval()
	if not hostOp:
		return
	prefix = filterOp.par.Installedlabelprefix.eval()
	page = hostOp.appendCustomPage('Param Filter')
	fp = filterOp.par.Parfilterenable
	page.appendToggle(fp.name, label=prefix + fp.label)
	fp = filterOp.par.Parfiltertype
	p = page.appendMenu(fp.name, label=prefix + fp.label)[0]
	p.menuNames = fp.menuNames
	p.menuLabels = fp.menuLabels
	p.default = fp.default
	_copyFloatPar(page, filterOp.par.Parfilterwidth, prefix)
	_copyFloatPar(page, filterOp.par.Parfilterlag1, prefix)
	_copyFloatPar(page, filterOp.par.Parfilterovershoot1, prefix)

	exprPrefix = 'op("{}").par.'.format(filterOp.relativePath(hostOp))
	for p in filterOp.customPages[0].pars:
		p.expr = exprPrefix + p.name

def _copyFloatPar(page: 'Page', src: 'Par', prefix: str):
	sourceTuplet = src.tuplet
	parTuplet = page.appendFloat(src.tupletName, label=prefix + src.label, size=len(sourceTuplet))
	for i, srcp in enumerate(sourceTuplet):
		for a in (
				'default', 'normMin', 'normMax',
				'clampMin', 'clampMax', 'min', 'max'
		):
			setattr(parTuplet[i], a, getattr(srcp, a))
