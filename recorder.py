import datetime
import os
import pathlib
import shutil

class Recorder:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp
		self.ImageFileName = tdu.Dependency('')
		self.VideoFileName = tdu.Dependency('')
		self.DiskSpace = tdu.Dependency('')
		self.UpdateDiskSpace()
		self.UpdateFileNames()

	def CaptureImage(self):
		self.UpdateFileNames()
		fileout = self.ownerComp.op('./imagefileout')
		fileout.par.record.pulse()
		ui.status = 'Wrote image to ' + fileout.par.file.eval()
		self.UpdateDiskSpace()

	def StartVideoCapture(self):
		self.UpdateFileNames()
		fileout = self.ownerComp.op('./moviefileout')
		fileout.par.record = True

	def EndVideoCapture(self):
		fileout = self.ownerComp.op('./moviefileout')
		fileout.par.record = False
		ui.status = 'Wrote video to ' + fileout.par.file.eval()
		self.UpdateDiskSpace()

	@property
	def _OutputFolderPath(self):
		folder = self.ownerComp.par.Folder.eval()
		if folder:
			folder = mod.tdu.expandPath(folder)
		return pathlib.Path(folder or project.folder)

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

	def UpdateFileNames(self):
		basename = self.ownerComp.par.Basename.eval()
		if not basename:
			basename = os.path.splitext(project.name)[0] + '-output'
		folder = self._OutputFolderPath
		basename += '-' + str(datetime.date.today())
		i = 1
		if folder.exists():
			while any(folder.glob(basename + str(i) + '[.-]*')):
				i += 1
		basename += '-' + str(i)
		if self.ownerComp.par.Suffix:
			basename += '-' + self.ownerComp.par.Suffix
		if self.ownerComp.par.Addresolutionsuffix:
			ressuffix = '-' + self._ResolutionSuffix
		else:
			ressuffix = ''
		self.ImageFileName.val = str(folder / (basename + ressuffix))
		if self.ownerComp.par.Videotype == 'imagesequence':
			self.VideoFileName.val = self.ImageFileName.val
		else:
			suffixes = []
			if self.ownerComp.par.Addvcodecsuffix:
				suffixes.append(self._VideoCodecSuffix)
			if self.ownerComp.par.Addacodecsuffix and self.ownerComp.op('./have_audio')[0]:
				suffixes.append(self.ownerComp.par.Audiocodec.eval())
			vid = basename + ressuffix
			if suffixes:
				vid += '-' + ('-'.join(suffixes))
			self.VideoFileName.val = str(folder / vid)

	@property
	def _ResolutionSuffix(self):
		if self.ownerComp.par.Useinputres:
			video = self.ownerComp.op('./video')
			w, h = video.width, video.height
		else:
			w, h = int(self.ownerComp.par.Resolution1), int(self.ownerComp.par.Resolution2)
		return '{}x{}'.format(w, h)

	@property
	def _VideoCodecSuffix(self):
		vcodec = self.ownerComp.par.Videocodec.eval()
		suffix = self.ownerComp.op('./video_codecs')[vcodec, 'suffix']
		return suffix.val if suffix and suffix.val else vcodec

	@property
	def ImageExtension(self):
		imgtype = self.ownerComp.par.Imagefiletype.eval()
		ext = self.ownerComp.op('./image_ext_overrides')[imgtype, 1]
		return ext.val if ext else imgtype

class Recorder2:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp

	def BuildImageFileName(self):
		folder = self._OutputFolderPath
		return self._BuildFileName(folder, isvideo=False, isimagesequence=False)

	def BuildImageSequenceFileName(self):
		folder = self._OutputFolderPath
		return self._BuildFileName(folder, isvideo=False, isimagesequence=True)

	def BuildVideoFileName(self):
		folder = self._OutputFolderPath
		return self._BuildFileName(folder, isvideo=True, isimagesequence=False)

	def _GetFileBaseName(self):
		name = self.ownerComp.par.Basename.eval()
		if not name:
			name = os.path.splitext(project.name)[0] + '-output'
		if self.ownerComp.par.Includedate:
			name += '-' + str(datetime.date.today())
		return name + '-'

	@property
	def _ResolutionSuffix(self):
		if self.ownerComp.par.Useinputres:
			video = self.ownerComp.op('./video')
			w, h = video.width, video.height
		else:
			w, h = int(self.ownerComp.par.Resolution1), int(self.ownerComp.par.Resolution2)
		return '{}x{}'.format(w, h)

	@property
	def _VideoCodecSuffix(self):
		vcodec = self.ownerComp.par.Videocodec.eval()
		suffix = self.ownerComp.op('./video_codecs')[vcodec, 'suffix']
		return suffix.val if suffix and suffix.val else vcodec

	@property
	def _ImageExtension(self):
		imgtype = self.ownerComp.par.Imagefiletype.eval()
		ext = self.ownerComp.op('./image_ext_overrides')[imgtype, 1]
		return ext.val if ext else imgtype

	@property
	def _HasAudio(self):
		return self.ownerComp.op('./have_audio')[0]

	def _GetSuffix(self, isvideo, isimagesequence):
		suffix = self.ownerComp.par.Suffix.eval()
		if self.ownerComp.par.Addresolutionsuffix:
			suffix = suffix + self._ResolutionSuffix
		if isvideo or isimagesequence:
			if self.ownerComp.par.Addvcodecsuffix:
				suffix += '-' + self._VideoCodecSuffix
			if self.ownerComp.par.Addacodecsuffix and self._HasAudio:
				suffix += '-' + self.ownerComp.par.Audiocodec
			if self.ownerComp.par.Addfpssuffix:
				suffix += '-' + self.ownerComp.par.Fps
		if isvideo:
			ext = '.mov'
		else:
			ext = '.' + self._ImageExtension
		if suffix:
			suffix = '-' + suffix
		return suffix + ext

	@property
	def _OutputFolderPath(self):
		folder = self.ownerComp.par.Folder.eval()
		if folder:
			folder = mod.tdu.expandPath(folder)
		return pathlib.Path(folder or project.folder)

	def _BuildFileName(self, folder: pathlib.Path, isvideo, isimagesequence):
		basename = self._GetFileBaseName()
		i = 1
		if folder.exists():
			while any(folder.glob(basename + str(i) + '[.-]*')):
				i += 1
		suffix = self._GetSuffix(isvideo, isimagesequence)
		return basename + str(i) + suffix

	@staticmethod
	def _CreateOutputFolder(folder):
		if folder.exists():
			ui.status = 'Output folder exists: {}'.format(folder)
		else:
			folder.mkdir(parents=True, exist_ok=True)
			ui.status = 'Created output folder: {}'.format(folder)

	def StartVideoCapture(self):
		folder = self._OutputFolderPath
		self._CreateOutputFolder(folder)
		if self.ownerComp.par.Videotype == 'imagesequence':
			filename = self.BuildImageSequenceFileName()
		else:
			filename = self.BuildVideoFileName()
		filepath = folder.joinpath(filename)
		ui.status = 'Start video capture ' + filepath
		fileout = self.ownerComp.op('./moviefileout')
		fileout.par.file = filepath
		fileout.par.record = True

	def EndVideoCapture(self):
		fileout = self.ownerComp.op('./moviefileout')
		fileout.par.record = False
		ui.status = 'Wrote video to ' + fileout.par.file.eval()

	def CaptureImage(self):
		folder = self._OutputFolderPath
		self._CreateOutputFolder(folder)
		filepath = folder.joinpath(self.BuildImageFileName())
		fileout = self.ownerComp.op('./moviefileout')
		fileout.par.file = filepath
		fileout.par.record.pulse()
		ui.status = 'Wrote image to ' + filepath

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
	project.name = ''
	project.folder = ''
	ui = _Dummy()
	ui.status = ''
	mod = _Dummy()
	mod.tdu = _Dummy()
	mod.tdu.expandPath = lambda _: _

	def op(_): pass

	def ops(*_): return []
