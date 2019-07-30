import datetime
import os
import pathlib
import shutil

from common import ExtensionBase, loggedmethod

_inputResMultipliers = {
	'quarter': 0.25,
	'half': 0.5,
	'original': 1,
	'double': 2,
	'quadruple': 4,
}

class Recorder(ExtensionBase):
	def __init__(self, ownerComp):
		super().__init__(ownerComp)
		self.DiskSpace = tdu.Dependency(None)
		if self.IsRecordingVideo:
			self.EndVideoCapture()

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
		if name.endswith('.toe'):
			name = name[:-4]
		if self.ownerComp.par.Includedate:
			name += '-' + str(datetime.date.today())
		return name + '-'

	@property
	def Resolution(self):
		if self.ownerComp.par.Useinputres:
			video = self.ownerComp.op('./video')
			multipliername = self.ownerComp.par.Inputresmult.eval()
			w, h = video.width, video.height
			mult = _inputResMultipliers.get(multipliername) or 1
			w = round(w * mult)
			h = round(h * mult)
		else:
			w, h = int(self.ownerComp.par.Resolution1), int(self.ownerComp.par.Resolution2)
		return w, h

	@property
	def FormattedResolution(self):
		w, h = self.Resolution
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
		suffixparts = [suffix] if suffix else []
		if self.ownerComp.par.Addresolutionsuffix:
			suffixparts.append(self.FormattedResolution)
		if isvideo or isimagesequence:
			if self.ownerComp.par.Addvcodecsuffix:
				suffixparts.append(self._VideoCodecSuffix)
			if self.ownerComp.par.Addacodecsuffix and self._HasAudio:
				suffixparts.append(self.ownerComp.par.Audiocodec.eval())
			if self.ownerComp.par.Addfpssuffix:
				suffixparts.append(str(self.ownerComp.par.Fps) + 'fps')
		if isvideo:
			ext = '.mov'
		else:
			ext = '.' + self._ImageExtension
		if not suffixparts:
			return ext
		return '-'.join([''] + suffixparts) + ext

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

	@property
	def _MovieOut(self):
		return self.ownerComp.op('moviefileout')

	@property
	def IsRecordingVideo(self):
		return self._MovieOut.par.record.eval()

	@loggedmethod
	def StartVideoCapture(self):
		folder = self._OutputFolderPath
		self._CreateOutputFolder(folder)
		if self.ownerComp.par.Videotype == 'imagesequence':
			filename = self.BuildImageSequenceFileName()
		else:
			filename = self.BuildVideoFileName()
		filepath = folder.joinpath(filename)
		ui.status = 'Start video capture ' + str(filepath)
		fileout = self._MovieOut
		fileout.par.file = filepath
		fileout.par.record = True

	@loggedmethod
	def EndVideoCapture(self):
		fileout = self._MovieOut
		fileout.par.record = False
		ui.status = 'Wrote video to ' + fileout.par.file.eval()

	@loggedmethod
	def CaptureImage(self):
		folder = self._OutputFolderPath
		self._CreateOutputFolder(folder)
		filepath = folder.joinpath(self.BuildImageFileName())
		fileout = self.ownerComp.op('video')
		fileout.save(filepath)
		ui.status = 'Wrote image to ' + str(filepath)

	def UpdateDiskSpace(self):
		folder = self._OutputFolderPath
		if not folder.exists():
			self.DiskSpace.val = None
		else:
			space = shutil.disk_usage(str(folder))
			self.DiskSpace.val = space.free

	@property
	def FormattedDiskSpace(self):
		val = self.DiskSpace.val
		return '' if val is None else _formatBytes(val)

	@loggedmethod
	def EmergencyShutOff(self):
		if not self.IsRecordingVideo:
			self._LogEvent('Not recording, nothing to stop')
			return
		msg = 'WARNING: halting recording due to insufficient disk space'
		self._LogEvent(msg)
		ui.status = 'WARNING: halting recording due to insufficient disk space'
		self.EndVideoCapture()

	def UpdatePanelHeight(self):
		height = _panelsHeight(self.ownerComp.op('root_panel').panelChildren)
		height += _panelsHeight(self.ownerComp.op('settings_panel').panelChildren)
		maxheight = self.ownerComp.par.Maxheight.eval()
		if 0 < maxheight < height:
			height = maxheight
		self.ownerComp.par.h = height

def _panelsHeight(panels):
	return sum([
		c.height
		for c in panels
		if c.isPanel and c.par.display and c.par.vmode == 'fixed'
	])

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
