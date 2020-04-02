class UIColorEditor:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
	
	@staticmethod
	def GetUIColors():
		return {
			key: ui.colors[key]
			for key in ui.colors
		}
	
	@staticmethod
	def BuildColorTable(dat):
		dat.clear()
		dat.appendRow(['name', 'r', 'g', 'b'])
		for key in sorted(ui.colors):
			dat.appendRow([key] + list(ui.colors[key]))

	def UpdateListColors(self, colorTable):
		colorList = self.ownerComp.op('color_list').par.Lister.eval()
		for i in range(1, colorTable.numRows):
			color = colorTable[i, 'r'], colorTable[i, 'g'], colorTable[i, 'b'], 1
			colorList.SetCellOverlay(i, 1, color)
			colorList.SetCellOverlay(i, 2, color)
			colorList.SetCellOverlay(i, 3, color)

		pass
