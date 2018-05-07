import pathlib
import shutil

class Recorder:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.ImageFileName = tdu.Dependency('')
		self.VideoFileName = tdu.Dependency('')
		self.DiskSpace = tdu.Dependency('')
		self.UpdateDiskSpace()

	def CaptureImage(self):
		pass

	def StartVideoCapture(self, imgSequence=False):
		pass

	def EndVideoCapture(self):
		pass

	@property
	def _OutputFolderPath(self):
		return pathlib.Path(self.ownerComp.par.Folder.eval() or project.folder)

	def CreateOutputFolder(self):
		folder = self._OutputFolderPath
		if folder.exists():
			ui.status = 'Output folder exists: {}'.format(folder)
		else:
			folder.mkdir(parents=True, exist_ok=True)
			ui.status = 'Created output folder: {}'.format(folder)
			self.UpdateDiskSpace()

	def UpdateDiskSpace(self):
		folder = self._OutputFolderPath
		if not folder.exists():
			self.DiskSpace.val = ''
		else:
			space = shutil.disk_usage(str(folder))
			self.DiskSpace.val = _formatBytes(space.free)

_sizes = ["B", "KB", "MB", "GB", "TB"]
def _formatBytes(bytes_num):

	i = 0
	dblbyte = bytes_num

	while i < len(_sizes) and bytes_num >= 1024:
		dblbyte = bytes_num / 1024.0
		i = i + 1
		bytes_num = bytes_num / 1024

	return str(round(dblbyte, 2)) + " " + _sizes[i]


# stubs

if False:
	class _Dummy:
		pass

	class Dependency:
		def __init__(self, _=None):
			self.val = None

		def modified(self): pass

	tdu = _Dummy()
	tdu.Dependency = Dependency
	project = _Dummy()
	project.folder = ''
	ui = _Dummy()
	ui.status = ''

	def op(_): pass

	def ops(*_): return []
