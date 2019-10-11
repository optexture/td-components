import os.path

def file(path):
	return path if os.path.exists(path) else ''

def modpath(*oppaths, checkprefix=None):
	for o in ops(*oppaths):
		if o.isDAT and o.isText and o.text and (not checkprefix or o.text.startswith(checkprefix)):
			return o.path
	return ''
