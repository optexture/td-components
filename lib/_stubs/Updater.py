"""
Extension classes enhance TouchDesigner components with python. An
extension is accessed via ext.ExtensionClassName from any operator
within the extended component. If the extension is promoted via its
Promote Extension parameter, all its attributes with capitalized names
can be accessed externally, e.g. op('yourComp').PromotedFunction().

Help: search "Extensions" in wiki
"""

from distutils.version import LooseVersion

from _stubs import *
from .TDStoreTools import StorageManager
TDF = op.TDModules.mod.TDFunctions
popDialog = op.TDResources.op('popDialog')

class Updater:
	"""
	Updater description
	"""
	def __init__(self, ownerComp):
		# The component to which this extension is attached
		self.ownerComp = ownerComp
		self.progressDialog = ownerComp.op('progressDialog')
		self.updateInfo = {}
		TDF.createProperty(self, 'UpdatesRemaining', value=0, dependable=True)
		TDF.createProperty(self, 'UpdatesQueued', value=0, dependable=True)
		TDF.createProperty(self, 'CurrentUpdateComp', value='', dependable=True)

	def onUpdateCompParValueChange(self, par, prev, updater):
		pass
		
	def onUpdateCompParPulse(self, par, updater):
		if par.name == 'Update':
			self.Update(par.owner, updater)

	def AbortUpdates(self):
		self.updateInfo = {}
		self.UpdatesRemaining = self.UpdatesQueued = 0
		print("*** Update Aborted ***")

	def Update(self, comps, updater=None, versionCheck='dialog',
			   		preUpdateMethod=None, postUpdateMethod=None,
			   		updateMethod=None):
		"""
		Update a component or components. Updating will pulse clone and set the
		component's version to the version on the clone source.

		:param comps: a single component or a list of components
		:param updater: the TDUpdateSystem component
		:param versionCheck: defines versioning behavior. 'dialog' = opens
			warning dialog if clone source version is lower, True =
			does not update if clone source version is lower, False = ignore
			versions
		:param preUpdateMethod: will be called before update with a single
			argument containing a dictionary of info
		:param postUpdateMethod: will be called after update with a single
			argument containing a dictionary of info
		:param updateMethod: will be called instead of standard update with a
			single argument containing a dictionary of info
		:return:
		"""
		if versionCheck not in ['dialog', True, False]:
			raise ValueError('versionCheck must be True, False, or "dialog"')
		info = self.updateInfo
		if isinstance(comps, COMP):
			comps = [comps]
		self.UpdatesRemaining += len(comps)
		self.UpdatesQueued += len(comps)
		if self.UpdatesQueued > 1:
			self.progressDialog.Open()
		updateInfo = {'queuedComps': comps,
						   'versionCheck': versionCheck,
						   'preUpdateMethod': preUpdateMethod,
						   'postUpdateMethod': postUpdateMethod,
						   'updateMethod': updateMethod,
						   'updater': updater}
		if info and info['queuedComps']:
			info['queuedInfo'].append(updateInfo)
		else:
			self.updateInfo = {'queuedComps': comps,
						   'versionCheck': versionCheck,
						   'preUpdateMethod': preUpdateMethod,
						   'postUpdateMethod': postUpdateMethod,
						   'updateMethod': updateMethod,
						   'updater': updater,
						   'queuedInfo': []}
			self.doNextUpdate()

	def doNextUpdate(self):
		info = self.updateInfo
		if not info:
			self.endUpdates()
			return
		comp = info['queuedComps'][0]
		self.CurrentUpdateComp = comp.path
		info['comp'] = comp
		if not isinstance(comp, COMP):
			raise TypeError("Invalid object sent to Update: " + str(comp))
		elif not comp.par.Update.enable:
			print('Skip update for', comp.path + '. Update disabled.\n')
			self.doNextUpdate()
			return
		else:
			if info['versionCheck'] is not False:
				source = comp.par.clone.eval()
				if source == comp:
					print("Can't update", comp.path + ". Component is it's own "
													  "clone source.")
					while comp in info['queuedComps']:
						info['queuedComps'].remove(comp)
					if not info['queuedComps']:
						self.endUpdates()
						return
					self.doNextUpdate()
					return
				if not source:
					sourceMessage = \
								info['updater'].par.Invalidsourcemessage.eval()\
										if info['updater'] else ''
					errorMessage = "Invalid clone source for " + comp.path +'.'
					if sourceMessage:
						errorMessage += ' ' + sourceMessage
					print(errorMessage)
					self.OpenErrorDialog()
					self.doNextUpdate()
					return
				oldVersion = comp.par.Version.eval()
				newVersion = source.par.Version.eval()
				if LooseVersion(oldVersion) > LooseVersion(newVersion):
					if info['versionCheck'] is True:
						self.versionSkip()
						return
					else:
						op.TDResources.op('popDialog').Open(
							text='Clone source for ' + comp.path +
								 ' has lower version. Update anyway?',
							title='Lower Version',
							buttons=['Yes', 'Yes All', 'No', 'No All'],
							callback=self.onVersionDialog,
							textEntry=False,
							escButton=3,
							enterButton=3,
							escOnClickAway=True
						)
						return
			self.startUpdate()

	def OpenErrorDialog(self):
		popDialog.OpenDefault(
			"There were errors running Update. See textport for details.",
			"Update Error",
			["OK"])

	def versionSkip(self):
		print('Skip update for',
			  self.updateInfo['comp'].path + '. Newer than source.\n')
		self.doNextUpdate()

	def onVersionDialog(self, info):
		if info['button'] == 'Yes':
			self.startUpdate()
		elif info['button'] == 'Yes All':
			self.updateInfo['versionCheck'] = False
			self.startUpdate()
		elif info['button'] == 'No':
			self.versionSkip()
		elif info['button'] == 'No All':
			self.updateInfo['versionCheck'] = True
			self.versionSkip()

	def startUpdate(self):
		info = self.updateInfo
		comp = info['comp']
		print('Updating', comp.path)
		if info['preUpdateMethod']:
			info['preUpdateMethod'](info)
		if info['updateMethod']:
			info['updateMethod'](info)
		else:
			self.updateMethod()
		if info['postUpdateMethod']:
			info['postUpdateMethod'](info)
		run('op(' + str(self.ownerComp.id) +
			').ext.Updater.updateComplete()', delayFrames=1,
			delayRef=op.TDResources)

	def updateMethod(self):
		info = self.updateInfo
		comp = info['comp']
		info['preUpdateAllowCooking'] = comp.allowCooking
		comp.allowCooking = False
		comp.par.enablecloningpulse.pulse()
		if comp.pars('Version') and comp.par.clone.eval().pars('Version'):
				comp.par.Version = comp.par.clone.eval().par.Version.eval()

	def endUpdates(self):
		self.progressDialog.Close()
		self.UpdatesRemaining = 0
		self.UpdatesQueued = 0
		self.updateInfo = []

	def updateComplete(self):
		if not self.updateInfo or not self.UpdatesRemaining:
			self.endUpdates()
			return
		self.UpdatesRemaining -= 1

		info = self.updateInfo
		if 'preUpdateAllowCooking' in info:
			info['comp'].allowCooking = info['preUpdateAllowCooking']
		print('   Update complete.\n')
		while info['comp'] in info['queuedComps']:
			info['queuedComps'].remove(info['comp'])
		if info['queuedInfo']:
			newInfo = info['queuedInfo'].pop(0)
			info.update(newInfo)
		if info['queuedComps']:
			run('op(' + str(self.ownerComp.id) +
				').ext.Updater.doNextUpdate()', delayFrames=1,
				delayRef=op.TDResources)
		else:
			self.endUpdates()


	def onUpdateSystemParValueChange(self, par, prev):
		system = par.owner
		comp = system.par.Comptoupdate.eval()
		if par.name == 'Enableupdatesystem':
			if comp.pars('Update'):
				comp.par.Update.enable = par.eval()

	def onUpdateSystemParPulse(self, par):
		system = par.owner
		comp = system.par.Comptoupdate.eval()
		if par.name == 'Setupparameters':
			self.SetupUpdateParameters(comp)
		elif par.name == 'Update':
			self.Update(comp)

	def SetupUpdateParameters(self, comp):
		"""
		Add Version and Update parameters to comp, if they aren't there already.
		They will be added to "Update" page, which will also be created, if
		necessary.

		:param comp: Component to add parameters to.
		:return:
		"""
		if isinstance(comp, COMP):
			if comp.pars('Version'):
				if not comp.par.Version.isString:
					raise TypeError('"Version" parameter not a string')
			else:
				if 'Update' not in comp.customPages:
					page = comp.appendCustomPage('Update')
				else:
					page = next((p for p in comp.customPages
								 					if p.name == 'Update'))
				page.appendStr('Version')
				comp.par.Version = '0.1'
				comp.par.Version.readOnly = True
			if comp.pars('Update'):
				if not comp.par.Update.isPulse:
					raise TypeError('"Update" parameter not a pulse')
			else:
				if 'Update' not in comp.customPages:
					page = comp.appendCustomPage('Update')
				else:
					page = next((p for p in comp.customPages
								 					if p.name == 'Update'))
				page.appendPulse('Update')
			print('Added Update parameters to', comp)
		else:
			raise TypeError('Can only setup parameters on COMP. Passed: ',
							str(comp))
