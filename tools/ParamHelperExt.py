# noinspection PyUnresolvedReferences
import tdu

# noinspection PyUnreachableCode
if False:
	from _stubs import *

class ParamHelper:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	@property
	def DestinationPageNames(self):
		d = self._Destination
		return [p.name for p in d.customPages] if d else []

	def HandleDrop(self, dropName, xPos, yPos, index, totalDragged, dropExt, baseName, destPath):
		print('ParamHelper HandleDrop {!r}'.format(locals()))
		if dropExt == 'parameter':
			o = op(baseName)
			par = getattr(o.par, dropName) if o else None
			if par is not None:
				self._ApplyChangesToParameter(par)
		elif dropExt in ('DAT', 'TOP', 'CHOP', 'SOP', 'MAT'):
			parentOp = op(baseName)
			o = parentOp.op(dropName) if parentOp else None
			if o is not None:
				self._HandleDropOp(o)
		pass

	def _HandleDropOp(self, o: 'OP'):
		pass

	@property
	def _Destination(self) -> 'COMP':
		return self.ownerComp.par.Destination.eval()

	def _UpdateStatus(self, message: str):
		ui.status = message
		statuses = self.ownerComp.op('set_statuses')
		statuses.appendRow([message])

	def _ApplyChangesToParameter(self, par: 'Par'):
		dest = self._Destination
		if not dest:
			self._UpdateStatus('No destination OP')
			return
		if not dest.isCOMP:
			self._UpdateStatus('Destination is not a COMP!')
			return
		namePrefix = self.ownerComp.par.Nameprefix.eval()
		if self.ownerComp.par.Labelusecustomprefix:
			labelPrefix = self.ownerComp.par.Labelprefix.eval()
		elif not namePrefix:
			labelPrefix = ''
		else:
			labelPrefix = namePrefix
		if labelPrefix and not labelPrefix.endswith(' '):
			labelPrefix += ' '
		namePrefix = tdu.legalName(namePrefix)
		newName = tdu.legalName(namePrefix + par.name).capitalize()
		label = labelPrefix + par.label
		if self.ownerComp.par.Pageusecustomname:
			pageName = self.ownerComp.par.Page.eval()
		else:
			pageName = par.page.name
		if not pageName:
			pageName = 'Custom'
		existingPar = getattr(dest.par, newName, None)
		if existingPar is not None:
			self._UpdateStatus('Updating existing parameter: {}'.format(newName))
			existingPar.label = label
			newPar = existingPar
		else:
			self._UpdateStatus('Attempting to get/create page: {!r}'.format(pageName))
			page = dest.appendCustomPage(pageName)
			self._UpdateStatus('Attempting to create par {!r}'.format(newName))
			newPar = page.appendPar(newName, par=par, label=label)[0]
			self._UpdateStatus('Created parameter {!r}'.format(newPar))
		attachType = self.ownerComp.par.Attachmenttype.eval()
		if attachType == 'none':
			return
		if self.ownerComp.par.Attachdirection == 'oldmaster':
			fromOp = dest
			toOp = par.owner
			fromPar = newPar
			toPar = par
		else:
			fromOp = par.owner
			toOp = dest
			fromPar = par
			toPar = newPar
		self._UpdateStatus('Attempting to connect {!r} to {!r} using {}'.format(
			toPar, fromPar, attachType))
		expr = self._GetParExpr(
			fromOp=fromOp, toOp=toOp, parName=toPar.name)
		self._UpdateStatus('Attempting to connect {!r} to {!r} using {}, expr: {!r}'.format(
			toPar, fromPar, attachType, expr))
		if not expr:
			return
		if attachType == 'binding':
			fromPar.bindExpr = expr
		elif attachType == 'reference':
			fromPar.expr = expr

	def _GetParExpr(self, fromOp: 'OP', toOp: 'OP', parName: str):
		pathType = self.ownerComp.par.Referencepathtype.eval()
		if pathType == 'absolute':
			return 'op({!r}).par.{}'.format(toOp.path, parName)
		elif pathType == 'relative':
			path = fromOp.relativePath(toOp)
			if not path:
				self._UpdateStatus('Unable to create relative path from {} to {}'.format(fromOp, toOp))
				return None
			return 'op({!r}).par.{}'.format(path, parName)
		else:
			path = fromOp.shortcutPath(toOp, toParName=parName)
			if not path:
				self._UpdateStatus('Unable to create shortcut path from {} to {}'.format(fromOp, toOp))
			return path
