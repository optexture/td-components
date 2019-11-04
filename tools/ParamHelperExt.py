
class ParamHelper:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	@property
	def DestinationPageNames(self):
		o = self.ownerComp.par.Destination.eval()
		return [p.name for p in o.customPages] if o else []
