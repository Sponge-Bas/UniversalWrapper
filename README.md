# UniversalWrapper
UniversalWrapper is a convenient shell wrapper for python, allowing you to interact with command line interfaces as if they were Python modules. UniversalWrapper now also supports async commands since version 2.0.

Tested on ubuntu only.

# Getting started

```bash
pip install UniversalWrapper
```

# Usage
Imagine you want to call
```bash
$ ls /home --recursive
```
from python. Rather than using `subprocess.check_output`, you can just
```python
from universalwrapper import ls
ls("/home", recursive=True)
```
UniversalWrapper uses a set of simple rules to convert python commands to bash commands. The default conversion rules are:
 - "_" is changed to "-" (see `uw_settings.divider` and `uw_settings.flag_divider`)
 - between classes (the .) a space is added (see `uw_settings.class_divider`)
 - A argument is converted to a string
 - Keyword arguments are converted to flags, if `arg=True`, only the flag is use (no arguments)
   if `arg=False` the flag is removed if it is present in `uw_settings.input_add`
 - Keyword arguments with list repeat the flag: `foo=['bar', 'bar']` calls `--foo bar --foo bar`

Repetitive commands or output modifications can be set `uw_settings`, see advanced usage.

# Examples

Below are some examples on how to use UniversalWrapper. Keep in mind, UniversalWrapper has no code specific to any particular command and the use of UniversalWrapper is in no way limited to the commands below.

If you are testing UniversalWrapper and prefer to not run the commands before you are familiar with the conversion rules, set `uw_settings.debug == True` and UniversalWrapper will print the command instead of executing it.

## Example: create and delete lxd containers

```python
from universalwrapper import lxc

lxc.launch("ubuntu:20.04", "testcontainer")
# calls $ lxc launch ubuntu:20.04 testcontainer

lxc.delete("testcontainer", force=True)
# calls $ lxc delete testcontainer --force
```

## Example: clone a library

```python
from universalwrapper import git

git.clone("https://github.com/Basdbruijne/UniversalWrapper.git")
# calls $ git clone https://github.com/Basdbruijne/UniversalWrapper.git
```
check git diff files:
```python
diff = git.diff(name_only=True)
# calls $ git diff --name-only
```

Commands can be chained as well (see `uw_settings.class_divider`):
```python
git.remote.rename("origin", "foo")
```

`True` and `False` flags are not forwarded to the cli. Instead `True` will add the flag only (without arguments) and `False` will remove the flag in case it is present elsewhere in the command. The latter can be useful is input overrides are used (see advanced usage). To avoid this behaviour, pass True or False as strings.

## Example: Async pip install

Async is enabled locally by the keyword `(_enable_async = True)`. To enable async globally, use `uw_settings.enable_async = True`.

Install pip requirements asynchronously

```python
import asyncio
from universalwrapper import pip

async def install_deps():
    install = await pip.install(requirement="requirements.txt", _enable_async = True)
    # Do other stuff while waiting for the install
    return await install

asyncio.run(install_deps())
```

## Example: send a notification

```python
from universalwrapper import notify_send

notify_send("title", "subtitle", i="face-wink")
# calls $ notify-sed title subtitle -i face-wink
```

The argument `(_root=True)` will trigger `sudo ` in the command.

# Advanced usage

The universal wrapper does not have any functions build in that are made for one specific cli. If there are repetitive modifications to commands that need to be made, this can be done by editing the uw_settings.
Some settings are global and some can also be used locally:

```python
from universalwrapper import foo

foo.uw_settings
>>
# Global settings
cmd: str = ""  # Base command
divider: str = "-"  # String to replace "_" with in commands
class_divider: str = " "  # String to place in between classes
flag_divider: str = "-"  # String to replace "_" with in flags
input_add: Dict[str:int] = {}  # {extra command, index where to add it}
input_move: Dict[str:int] = {}  # {extra command, index where to move it}
input_custom: List[str] = []  # custom command: e.g. "command.reverse()"

# Local or global settings
root: bool = False  # Run commands as sudo, same as `input_add={0: "sudo"}`
debug: bool = False  # Don't run commands but instead print the command
double_dash: bool = True  # Use -- instead of - for multi-character flags
enable_async: bool = False  # Globally enable asyncio
return_stderr: bool = False # Forward stderr output to the return values
output_parser: str = ""  # Output parser (yaml, json, splitlines, auto)
warn_stderr: bool = True # Forward stderr output to warnings
cwd: str = None  # Current working directory
env: str = None  # Env for environment variables
parallel: bool = False  # run subprocess in background, but without async
```

To use a global setting, assign the desired variable to `uw_settings`:
```python3
from universalwrapper import foo

foo.uw_settings.class_divider = "."
foo.uw_settings.enable_async = True
```

To use a local setting, use it as a keyword argument with a leading underscore:
```python3
from universalwrapper import foo

foo.bar(_output_parser = "yaml")
```

# Limitations

Not all commands can be called cleanly with UniversalWrapper, for example:
```bash
example --log-level Debug command --flag value separate_value
```
Can only be called with
```python
from uw import example
example("--log-level", "Debug", "command", "--flag", "value", "separate_value")
```
due to the limitation in python that keywords arguments must come after non-keyword arguments.
UniversalWrapper V3 may contain workarounds for this.

UniversalWrapper is in Beta and may be subjected to changes. 
