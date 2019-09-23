# Command Panel

The command panel is a configurable toolbar for invoking scripts.

The original use case was for editor shortcuts, like opening panel viewers or output windows, aligning selected OPs,
and so on. But it was designed to be reusable for a variety of purposes.

The panel loads a list of commands that each have an executable action, and a label and/or icon TOP.
It generates a button for each command with the relevant text/icon and runs the associated script when it is clicked.

## Specifying commands

There are several ways to specify commands for the panel.

1. Providing a table DAT via the "Command Table" parameter.
2. Specifying a list of `dict`s using the "Command Object List" parameter.
3. Enabling predefined lists of common commands, via the "Include ___ Commands" parameters.

### Using a command table

Each row after the first row is converted to a `dict`, with the columns as keys. See the next section for how those are
handled.

### Using `dict`s

Each `dict` in a list represents a single command. The following settings are available for all (or many) types of
commands:

* `label` (required) - text to put in the button
* `img` - optional TOP path for an image to show in the button
* `isIcon` - if true, and there's no `img`, `label` is interpreted as an icon character in the Material Design Icons.
* `help` - help text for the button
* `type` - specifies what type of pre-defined action to use (see below)

#### Command types

* *(none)* - the `action` setting is interpreted as a reference to an executable Python function
* `open` or `view` - opens an operator viewer or window for the specified `op`
 * `unique` - should the viewer be opened as a unique viewer for the op, defaults to true (not available for windows)
 * `borders` - should the viewer have window borders, defaults to true
* `toggle` - equivalent to `open`/`view` but if the viewer is already open, it closes it
* `pars` - open a parameter editor for the `op`
* `edit` or `navigate` - opens the `op` in the network editor, reusing the main editor if possible
* `run` - execute the `op` (must be a text DAT)
* `script` - execute a string of python code, from the `script` setting. Note that if you omit the `type` entirely but
  have a `script` field, the type is assumed to be `script`
* `reload` - reload the `op` (which can be multiple ops) from their associated files (such as text/table DATs)
* `save` - saves either the selected COMPs or the COMP that the network editor is in as a tox


### Using script text DATs

The `Cmdscripts` paramter can be used to specify a list of text DATs that each contain a script to run as a command.
If the script has a `def action(...)` in it, the script is treated as a module, and it can specify settings by declaring
them as variables. Otherwise the script is treated as a single block of executable code (using `theScriptDAT.run()`).

DAT with just a raw chunk of code:
```
op('/whatever/foo').par.Stuff = 'things'
print('hello!')
```

DAT with a function and settings:
```
label = 'some command'
help = 'do stuff with a script'
def action():
	print('hello!')
```


## Command `Context`

Command functions can optionally accept an argument that's generated by the panel, which provides access to shortcuts
and helper functions based on the editor context (what OPs are selected in the network editor, etc).