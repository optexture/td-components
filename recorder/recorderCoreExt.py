from pathlib import Path
import os
import datetime

# noinspection PyUnreachableCode
if False:
	# noinspection PyUnresolvedReferences
	from _stubs import *


class RecorderCore:
	def __init__(self, ownerComp):
		self.ownerComp = ownerComp  # type: COMP
		self.processedVideo = ownerComp.op('video')
		self.movieOut = ownerComp.op('moviefileout')
		self.imageOut = ownerComp.op('imagefileout')
		self.videoRes = ownerComp.op('video_res')
		self.audioState = ownerComp.op('audio_state')

	@property
	def formattedResolution(self):
		w = int(self.videoRes['width'])
		h = int(self.videoRes['height'])
		return f'{int(w)}x{int(h)}'

	@property
	def videoCodecSuffix(self):
		vcodec = self.ownerComp.par.Videocodec.eval()
		suffix = self.ownerComp.op('./video_codecs')[vcodec, 'suffix']
		if suffix is None:
			return vcodec
		return suffix.val

	@property
	def imageExtension(self):
		imgtype = self.ownerComp.par.Imagefiletype.eval()
		extension = self.ownerComp.op('./image_ext_overrides')[imgtype, 1]
		return extension.val if extension else imgtype

	@property
	def haveAudio(self):
		return self.audioState['haveaudio'] > 0

	def getSuffix(self, fileType):
		suffix = self.ownerComp.par.Suffix.eval()
		suffixParts = [suffix] if suffix else []
		if self.ownerComp.par.Addresolutionsuffix:
			suffixParts.append(self.formattedResolution)
		if fileType in ['movie', 'imagesequence']:
			if self.ownerComp.par.Addvcodecsuffix:
				vcSuffix = self.videoCodecSuffix
				if vcSuffix:
					suffixParts.append(vcSuffix)
			if self.ownerComp.par.Audioenabled and self.ownerComp.par.Addacodecsuffix and self.haveAudio:
				suffixParts.append(self.ownerComp.par.Audiocodec.eval())
			if self.ownerComp.par.Addfpssuffix:
				suffixParts.append(str(self.ownerComp.par.Fps) + 'fps')
		if fileType == 'movie':
			extension = '.mov'
		else:
			extension = '.' + self.imageExtension
		if not suffixParts:
			return extension
		return '-'.join([''] + suffixParts) + extension

	@property
	def outputFolderPath(self):
		folder = self.ownerComp.par.Folder.eval()
		if folder:
			folder = mod.tdu.expandPath(folder)
		return Path(folder or project.folder)

	@property
	def fileBaseName(self):
		name = self.ownerComp.par.Basename.eval()
		if not name:
			name = os.path.splitext(project.name)[0] + '-output'
		if name.endswith('.toe'):
			name = name[:-4]
		if self.ownerComp.par.Includedate:
			dateMode = self.ownerComp.par.Datetype.eval()
			if dateMode == 'custom':
				dateValue = self.ownerComp.par.Customdate.eval()
			else:
				dateValue = str(datetime.date.today())
			if dateValue:
				name += '-' + dateValue
		return name + '-'

	def buildFileName(self, fileType):
		baseName = self.fileBaseName
		i = 1
		folder = self.outputFolderPath
		if folder.exists():
			existingFiles = folder.glob(baseName + '[0-9]*')
			maxIndex = None
			for file in existingFiles:
				try:
					fileIndex = int(file.stem[len(baseName):].split('-', 1)[0])
				except ValueError:
					continue
				if maxIndex is None or fileIndex > maxIndex:
					maxIndex = fileIndex
			if maxIndex is not None:
				i = maxIndex + 1
		suffix = self.getSuffix(fileType)
		return baseName + str(i) + suffix

	def CreateOutputFolder(self):
		folder = self.outputFolderPath
		if folder.exists():
			# ui.status = 'Output folder exists: {}'.format(folder)
			pass
		else:
			folder.mkdir(parents=True, exist_ok=True)
			ui.status = 'Created output folder: ' + str(folder)
		return folder

	def BuildImageFileName(self):
		return self.buildFileName('image')

	def BuildVideoFileName(self):
		return self.buildFileName('movie')

	def BuildImageSequenceFileName(self):
		return self.buildFileName('imagesequence')

	def StartVideoCapture(self):
		folder = self.CreateOutputFolder()
		if self.ownerComp.par.Videotype == 'imagesequence':
			fileName = self.BuildImageSequenceFileName()
		else:
			fileName = self.BuildVideoFileName()
		filePath = folder.joinpath(fileName)
		ui.status = 'Start video capture ' + str(filePath)
		self.movieOut.par.file = filePath
		self.movieOut.par.record = True

	def EndVideoCapture(self):
		if not self.movieOut.par.record:
			return
		self.movieOut.par.record = False
		ui.status = 'Wrote video to ' + str(self.movieOut.par.file)
		self.movieOut.par.file = ''

	def CaptureImage(self):
		folder = self.CreateOutputFolder()
		filePath = folder.joinpath(self.BuildImageFileName())
		self.imageOut.par.file = filePath
		self.imageOut.par.record.pulse(1)
		ui.status = 'Wrote image to ' + str(filePath)
		self.imageOut.par.file = ''


