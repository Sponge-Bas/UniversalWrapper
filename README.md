# UniversalWrapper
Use any shell command in python conveniently.

Based on subprocess, the universal wrapper provides an intuitive wrapper around any cli.
Tested on ubuntu only. The development is inspired by my jealousy toward bash scripts, where command line tools can be integrated seamlessly into the code. This tool provides a similar level of integration, without having to manually write wappers for the specific cli's. 

# Getting started

```bash
pip install UniversalWrapper
```

# Examples
## Example: create and delete lxd containers

```python
from universalwrapper import lxc

lxc.launch("ubuntu:20.04", "testcontainer")

lxc.delete("testcontainer", force=True)
```

## Example: clone a library

```python
from universalwrapper import git

git.clone("https://github.com/Basdbruijne/UniversalWrapper.git")
```
check git diff files:
```python
diff = git.diff(name_only=True)
```
`True` and `False` flags are not forwarded to the cli. Instead `True` will add the flag only (without arguments) and `False` will remove the flag in case it is present elsewhere in the command. The latter can be useful is input overrides are used (see advanced usage). To avoid this behaviour, pass True or False as strings.

## Example: send a notification

```python
from universalwrapper import notify_send

notify_send("title", "subtitle", i="face-wink")
```

The argument `(root=True)` will trigger `sudo ` in the command.

# Advanced usage

The universal wrapper does not have any functions build in that are made for one specific cli. If there are repetitive modifications to commands that need to be made, this can be done by editing the uw_settings:

```python
from universalwrapper import lxc

lxc.uw_settings
>>
lxc.uw_settings["cmd"]: str # base command
lxc.uw_settings["divider"]: str = '-' # string to replace '_' with in command
lxc.uw_settings["class_divider"]: str = ' ' # string to put between classes
lxc.uw_settings["flag_divider"]: str = '-' # string to replace '_' with in flags
lxc.uw_settings["debug"]: bool = False # if True, don't execute command but just print it
lxc.uw_settings["input_modifiers"]: dict = { # order matters!
    "add": dict: {str: int, str: int} = {} # {extra command, index where to add it}
    "move": dict: {str: int, str: int} = {} # {extra command, index where to move it to}
    "custom": list[str] # custom command: e.g. "command.reverse()"
},
lxc.uw_settings["output_modifiers"]: dict = { # speaks for itself mostly, order matters!
    "decode": bool = True,
    "split_lines": bool = False,
    "parse_yaml": bool =  False,
    "parse_json": bool = False,
    "custom": list[str], # custom command: e.g. "output = output.upper()"
}
```