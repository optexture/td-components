# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *

# _resModeMultipliers = {
# 	'eighth': 0.125,
# 	'quarter': 0.25,
# 	'half': 0.5,
# 	'useinput': 1,
# 	'2x': 2,
# 	'4x': 4,
# 	'8x': 8,
# }

class RecorderCore:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP
		self.processedVideo = ownerComp.op('video')
		self.movieOut = ownerComp.op('moviefileout')
		self.imageOut = ownerComp.op('imagefileout')

	def GetResolution(self):
		mode = self.ownerComp.par.Outputresolution.eval()
		if mode == 'custom':
			return self.ownerComp.par.Resolution1.eval(), self.ownerComp.par.Resolution2.eval()
		return self.processedVideo.width, self.processedVideo.height


