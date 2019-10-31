# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

# + prefix marks the params 'advanced'
_prefix = '+'

def InitHost():
	filter = parent()
	hostop = filter.par.Parfilterop.eval()
	if not hostop:
		return
	prefix = filter.par.Installedlabelprefix.eval()
	page = hostop.appendCustomPage('Param Filter')
	fp = filter.par.Parfilterenable
	page.appendToggle(fp.name, label=prefix + fp.label)
	fp = filter.par.Parfiltertype
	p = page.appendMenu(fp.name, label=prefix + fp.label)[0]
	p.menuNames = fp.menuNames
	p.menuLabels = fp.menuLabels
	p.default = fp.default
	_copyFloatPar(page, filter.par.Parfilterwidth, prefix)
	_copyFloatPar(page, filter.par.Parfilterlag1, prefix)
	_copyFloatPar(page, filter.par.Parfilterovershoot1, prefix)

	relpath = filter.relativePath(hostop)
	exprprefix = 'op({!r}).par.'.format(relpath)
	for p in filter.customPages[0].pars:
		p.expr = exprprefix + p.name

def _copyFloatPar(page, src, prefix):
	srctup = src.tuplet
	ptup = page.appendFloat(src.tupletName, label=prefix + src.label, size=len(srctup))
	for i, srcp in enumerate(srctup):
		for a in (
				'default', 'normMin', 'normMax',
				'clampMin', 'clampMax', 'min', 'max'
		):
			setattr(ptup[i], a, getattr(srcp, a))
