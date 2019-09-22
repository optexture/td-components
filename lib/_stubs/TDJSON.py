# This file and all related intellectual property rights are
# owned by Derivative Inc. ("Derivative").  The use and modification
# of this file is governed by, and only permitted under, the terms
# of the Derivative [End-User License Agreement]
# [https://www.derivative.ca/Agreements/UsageAgreementTouchDesigner.asp]
# (the "License Agreement").  Among other terms, this file can only
# be used, and/or modified for use, with Derivative's TouchDesigner
# software, and only by employees of the organization that has licensed
# Derivative's TouchDesigner software by [accepting] the License Agreement.
# Any redistribution or sharing of this file, with or without modification,
# to or with any other person is strictly prohibited [(except as expressly
# permitted by the License Agreement)].
#
# Version: 099.2017.30440.28Sep
#
# _END_HEADER_

import json
import collections

def jsonToText(jsonObject):
	"""
	Return a JSON object as text
	"""
	return json.dumps(jsonObject, indent='\t')

def jsonToDat(jsonObject, dat):
	"""
	Write a JSON object into a dat.
	"""
	dat.text = jsonToText(jsonObject)

def textToJSON(text, orderedDict=True, showErrors=False):
	"""
	Turn a JSON object stored as text into a Python object.
	Will be forced to a Python collections.OrderedDict if orderedDict argument
	is True.
	"""
	try:
		if orderedDict:
			return json.loads(text, object_pairs_hook=collections.OrderedDict)
		else:
			return json.loads(text)
	except:
		if showErrors:
			raise
		else:
			return None

def datToJSON(dat, orderedDict=True, showErrors=False):
	"""
	Returns a JSONable dict from a dat
	"""
	return textToJSON(dat.text, orderedDict, showErrors)

def parameterToJSONPar(p, extraAttrs=None, forceAttrLists=False):
	"""
	Convert a parameter or tuplet to a jsonable python dictionary.
	extraAttrs: a list or tuple of attribute names that are not normally
		stored. For example, 'val' and 'order'.
	forceAttrLists: If True, all attributes will be stored in a list with the
		length of the tuplet
	NOTE: a parameter that is a member of a multi-value tuplet will create a
		JSON for the entire tuplet.
	"""
	parAttrs = ('name', 'label', 'page', 'style', 'size', 'default', 'enable',
				'startSection', 'cloneImmune', 'readOnly')
	numAttrs = ('min', 'max', 'normMin', 'normMax', 'clampMin', 'clampMax')
	# just grab the first parameter if it's a tuplet...
	if isinstance(p, tuple):
		p = p[0]

	# set up special par types
	if p.isMenu:
		if p.menuSource:
			parAttrs += ('menuSource',)
		else:
			parAttrs += ('menuNames', 'menuLabels')
	if p.isNumber:
		parAttrs += numAttrs
	if extraAttrs:
		parAttrs += tuple(extraAttrs)

	# create dictionary
	jDict = collections.OrderedDict()
	# grab attrs
	for attr in parAttrs:
		if attr == 'page' and p.isCustom:
			jDict['page'] = p.page.name
		elif attr == 'size':
			if p.style in ('Int', 'Float'):
				jDict['size'] = len(p.tuplet)
		elif attr == 'name':
			jDict['name'] = p.tupletName
		elif attr == 'menuSource':
			jDict['menuSource'] = p.menuSource or ''
		elif attr == 'mode':
			jDict['mode'] = str(p.mode)
		else:
			try:
				jDict[attr] = getattr(p, attr)
			except:
				pass
	# deal with multi-value parameter stuff
	if forceAttrLists or len(p.tuplet) > 1:
		for attr in (numAttrs + ('default', 'val', 'expr', 'mode',
								 'bindExpr')):
			if attr not in numAttrs and attr not in parAttrs:
				continue
			attrList = []
			for multiPar in p.tuplet:
				if attr == 'mode':
					attrList.append(str(multiPar.mode))
				else:
					attrList.append(getattr(multiPar, attr))
			# if we have any differing values, store all as list
			if forceAttrLists or len(set(attrList)) > 1:
				jDict[attr] = attrList
	return jDict

def pageToJSONDict(page, extraAttrs=None, forceAttrLists=False):
	"""
	Convert a page of parameters to a jsonable python dict.
		Format: {parameter name: {parameter attributes, ...}, ...}
	extraAttrs is a list or tuple of par attribute names that are not normally
		stored. For example, 'val' and 'order'.
	forceAttrLists: If True, all attributes will be stored in a list with the
		length of the tuplet
	"""
	jPage = collections.OrderedDict()
	for p in page.pars:
		# make sure we only do first par in each tuplet
		# and you must test by name otherwise it defaults to value tests
		if p.name == p.tuplet[0].name:
			jPage[p.tupletName] = parameterToJSONPar(p, extraAttrs,
													 forceAttrLists)
	return jPage

def opToJSONOp(op, extraAttrs=None, forceAttrLists=False):
	"""
	Convert all custom parameter pages to a jsonable python dict. Format:
		{page name: {parameter name: {parameter attributes, ...}, ...}, ...}
	extraAttrs is a list or tuple of par attribute names that are not normally
		stored. For example, 'val' and 'order'.
	forceAttrLists: If True, all attributes will be stored in a list with the
		length of the tuplet
	"""
	jOp = collections.OrderedDict()
	for page in op.customPages:
		jOp[page.name] = pageToJSONDict(page, extraAttrs,
										forceAttrLists)
	return jOp

def addParameterFromJSONDict(comp, jsonDict, replace=True, setValues=True,
							 ignoreAttrErrors=False):
	"""
	Add a parameter to comp as defined in a parameter JSON dict.
	If replace is False, will error out if the parameter already exists
	If setValues is True, values will be set to parameter's defaults
	If ignoreAttrErrors is True, no exceptions for bad attrs in json

	returns a list of newly created parameters
	"""
	requiredKeys = {'page', 'style', 'name'}
	# issubset checks par dict for the required keys of the set requiredKeys
	if requiredKeys.issubset(jsonDict):
		pStyle = jsonDict['style']
		parName = jsonDict['name']
		pageName = jsonDict['page']
	else:
		raise ValueError ('Parameter definition missing required '
						  'attributes. (' + str(requiredKeys) + ')',
						  jsonDict)
	label = jsonDict.get('label', parName)
	# set up page if necessary
	page = None
	for cPage in comp.customPages:
		if cPage.name == pageName:
			page = cPage
			break
	if page is None:
		page = comp.appendCustomPage(pageName)
	try:
		appendFunc = getattr(page, 'append' + pStyle )
	except:
		raise ValueError("Invalid parameter type in JSON dict", pStyle)

	size = jsonDict.get('size', 1)
	# check if we can just replace an already exising parameter
	newPars = None
	if replace:
		if size > 1 or len(Page.styles[pStyle].suffixes) > 1:
			# special search for multi-value pars
			checkPars = comp.pars(parName + '*')
			if checkPars:
				checkPar = checkPars[0]
				if checkPar.tupletName == parName and \
						checkPar.style == pStyle \
						and len(checkPar.tuplet) == size:
					newPars = checkPar.tuplet
		elif hasattr(comp.par, parName) and \
							getattr(comp.par, parName).style == pStyle\
				and len(getattr(comp.par, parName).tuplet) == 1:
			newPars = getattr(comp.par, parName).tuplet
	# create parameter and stash newly created parameter(s) if necessary
	if newPars is None:
		if size == 1:
			newPars = appendFunc(parName, label=label, replace=replace)
		else:
			newPars = appendFunc(parName, label=label, size=size,
								 								replace=replace)
	else:
		newPars[0].label = label
		newPars[0].page = page

	# set additional attributes if they're in parDict
	# can have multi-vals:
	listAttributes = ('default', 'min', 'max', 'normMin', 'normMax', 'clampMin',
					  'clampMax', 'val', 'expr', 'bindExpr', 'mode')
	for index, newPar in enumerate(newPars):
		# go through other attributes
		if setValues and not jsonDict.get('val'):
			try:
				try:
					newPar.val = jsonDict['default']
				except:
					newPar.val = newPar.default
			except:
				if ignoreAttrErrors:
					pass
				else:
					raise
		for attr, value in list(jsonDict.items()) + \
				([('mode', jsonDict['mode'])] if 'mode' in jsonDict else []):
			if attr in ['style', 'name', 'label', 'size', 'page']:
				continue
			try:
				# apply attributes that can contain an item or a list
				if attr in listAttributes:
					if isinstance(value, (list, tuple)):
						if attr == 'mode':
							setattr(newPar, attr,
									getattr(ParMode, value[index]))
						else:
							try:
								setattr(newPar, attr, value[index])
							except:
								debug(newPar, attr, value)
					elif attr == 'mode':
						setattr(newPar, attr, getattr(ParMode, value))
					else:
						setattr(newPar, attr, value)
				# apply standard attributes
				else:
					setattr(newPar, attr, value)

			except:
				if ignoreAttrErrors:
					pass
				else:
					raise
		# default menu labels to menu names
		if 'menuNames' in jsonDict and 'menuLabels' not in jsonDict:
			newPar.menuLabels = jsonDict['menuNames']
	return newPars

def addParametersFromJSONList(comp, jsonList, replace=True, setValues=True,
							  destroyOthers=False, newAtEnd=True):
	"""
	Add parameters to comp as defined in list of parameter JSON dicts.
	If replace is False, will cause exception if the parameter already exists
	If setValues is True, values will be set to parameter's defaults.
	If destroyOthers is True, pars and pages not in jsonList will be destroyed
	If newAtEnd is True, new parameters will be sorted to end of page. This
		should generally be False if you are using 'order' attribute in JSON
	"""
	parNames = []
	pageNames = set()
	for jsonPar in jsonList:
		newPars = addParameterFromJSONDict(comp, jsonPar, replace, setValues)
		parNames += [p.name for p in newPars]
		pageNames.add(newPars[0].page.name)
	if destroyOthers:
		destroyOtherPagesAndParameters(comp, pageNames, parNames)
	if newAtEnd:
		sortNewPars(comp, pageNames, parNames)
	return parNames, pageNames

def addParametersFromJSONDict(comp, jsonDict, replace=True, setValues=True,
							  destroyOthers=False, newAtEnd=True):
	"""
	Add parameters to comp as defined in dict of parameter JSON dicts.
	If replace is False, will error out if the parameter already exists
	If setValues is True, values will be set to parameter's defaults.
	If destroyOthers is True, pars and pages not in jsonDict will be destroyed
	If newAtEnd is True, new parameters will be sorted to end of page. This
		should generally be False if you are using 'order' attribute in JSON
	"""
	parNames = []
	pageNames = set()
	for jsonPar in jsonDict.values():
		newPars = addParameterFromJSONDict(comp, jsonPar, replace, setValues)
		parNames += [p.name for p in newPars]
		pageNames.add(newPars[0].page.name)
	if destroyOthers:
		destroyOtherPagesAndParameters(comp, pageNames, parNames)
	if newAtEnd:
		sortNewPars(comp, pageNames, parNames)
	return parNames, pageNames

def addParametersFromJSONOp(comp, jsonOp, replace=True, setValues=True,
							  destroyOthers=False, newAtEnd=True):
	"""
	Add parameters to comp as defined in dict of page JSON dicts.
	If replace is False, will error out if the parameter already exists
	If setValues is True, values will be set to parameter's defaults.
	If destroyOthers is True, pars and pages not in jsonOp will be destroyed
	If newAtEnd is True, new parameters will be sorted to end of page. This
		should generally be False if you are using 'order' attribute in JSON
	"""
	parNames = []
	pageNames = set()
	for jsonPage in jsonOp.values():
		newParNames, newPages = addParametersFromJSONDict(comp, jsonPage,
										replace, setValues, newAtEnd=newAtEnd)
		parNames += newParNames
		pageNames.update(newPages)
	if destroyOthers:
		destroyOtherPagesAndParameters(comp, pageNames, parNames)
	if newAtEnd:
		sortNewPars(comp, pageNames, parNames)
	return parNames, pageNames

def destroyOtherPagesAndParameters(comp, pageNames, parNames):
	"""
	Destroys all pages and parameters on comp that are not found in pageNames
	or parNames
	"""
	for p in comp.customPars:
		try:
			if p.name not in parNames:
				p.destroy()
		except Exception as e:
			# already destroyed
			# debug(e)
			continue
	for page in comp.customPages:
		if page.name not in pageNames:
			try:
				page.destroy()
			except:
				# already destroyed
				continue

def sortNewPars(comp, pageNames, parNames):
	"""
	Sorts the new parameters in added order at end of page
	"""
	pageDict = {page.name:{'oldPars':[], 'newPars':[]}
												for page in comp.customPages}
	for parName in parNames:
		par = getattr(comp.par, parName)
		if par.tupletName not in pageDict[par.page.name]['newPars']:
			pageDict[par.page.name]['newPars'].append(par.tupletName)
	for page in comp.customPages:
		info = pageDict[page.name]
		if not info['newPars']:
			continue
		for par in page.pars:
			if par.tupletName not in info['newPars']:
				if par.tupletName not in info['oldPars']:
					info['oldPars'].append(par.tupletName)
		page.sort(*(info['oldPars'] + info['newPars']))