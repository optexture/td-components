"""
TopMenu callbacks

Callbacks always take a single argument, which is a dictionary
of values relevant to the callback. Print this dictionary to see what is
being passed. The keys explain what each item is.

TopMenu info keys:
	'widget': the TopMenu widget
	'item': the item label in the menu list
	'index': either menu index or -1 for none
	'indexPath': list of parent menu indexes leading to this item
	'define': TopMenu define DAT definition info for this menu item
	'menu': the popMenu component inside topMenu
"""

#################################
# exampleMenuDefine callbacks

def onQuit(info):
	"""
	A simple menu item callback, named in the Top Menu DAT table
	"""
	debug('QUIT!')

guides = False
grid = True

def onSetting(info):
	"""
	A menu item callback that works on multiple menu items. The checkboxes in
	the menu evaluate the global guides and grid variables above to determine
	their state. The expressions used to evaluate the checkbox state are
	defined in the Top Menu DAT.
	"""
	global guides, grid
	if info['item'] == 'Show Guides':
		guides = not guides
	elif info['item'] == 'Show Grid':
		grid = not grid

def getRecentFiles(info):
	"""
	A rowCallback used in the Top Menu DAT table to automatically generate rows.
	These callbacks must return a dictionary or list of dictionaries that mimic
	the columns in the Top Menu DAT. Dictionaries only need the columns with
	data in them, but must have corresponding columns in the Top Menu DAT in
	order to be recognized.
	"""
	return [
		{'item2': 'File 1'},
		{'item2': 'File 2', 'highlight': True},
		{'item2': 'File three', 'dividerAfter': True}
	]

# end examples
####################################

def onItemTrigger(info):
	ext.editor.OnMenuTrigger(**info)

# standard menu callbacks

def onSelect(info):
	"""
	User selects a menu option
	"""
	debug(info)

def onRollover(info):
	"""
	Mouse rolled over an item
	"""

def onOpen(info):
	"""
	Menu opened
	"""

def onClose(info):
	"""
	Menu closed
	"""

def onMouseDown(info):
	"""
	Item pressed
	"""

def onMouseUp(info):
	"""
	Item released
	"""

def onClick(info):
	"""
	Item pressed and released
	"""

def onLostFocus(info):
	"""
	Menu lost focus
	"""