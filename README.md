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
from UniversalWrapper import UniversalWrapper as uw

lxc = uw('lxc')
lxc.launch("ubuntu:20.04", "testcontainer")

lxc.delete("testcontainer", force=True)
```

## Example: clone a library

```python
git = uw('git', divider='-')
git.clone("https://github.com/Basdbruijne/UniversalWrapper.git")
```
check git diff files:
```python
diff = git.diff(name_only=True)
```
Here, the `divider` specifies how different cli's define between words, underscores in the command will be transformed into the divider. A `class_divider` can also be defined, the dots between classes will be transformed to the class divider. By default `divider=" ", class_divider=" "`.

For example, `example=uw("example",divider = "-", class_divider = "=")` will result in `example.about.class_dividers()` calling `example=about=class-dividers`.

`True` and `False` flags are not forwarded to the cli. Instead `True` will add the flag only (without arguments) and `False` will remove the flag in case it is present elsewhere in the command. The latter can be useful is input overrides are used (see advanced usage). To avoid this behaviour, pass True or False as strings.

## Example: send a notification

```python
notify_send=uw('notify-send')
notify_send("title", "subtitle", i="face-wink")
```

The argument `(root=True)` will trigger `sudo ` in the command.

# Advanced usage

The universal wrapper does not have any functions build in that are made for one specific cli. If there are repetitive modifications to commands that need to be made, this can be done by inheriting the UniversalWrapper class:

```python
from UniversalWrapper import UniversalWrapper as uw

class Example(uw):
    def run_cmd(self, command):
    """
    Change this function if instead of subprocess.check_output a different
    package needs to be used.
    """
        command = self.input_modifier(command)
        output = subprocess.check_output(command, shell=True)
        return self.output_modifier(output)

    def input_modifier(self, command):
    """
    Change this function to define custom actions that need to be applied
    on every input.
    """
        return command

    def output_modifier(self, output):
    """
    Change this function to apply some custom processing on every command 
    output.
    """
        return output.decode("ascii")
        
example = Example('example')
```

# Limitations:
 - positional argument cannot follow keyword argument, for example:
```python
notify_send("title", "subtitle", i="face-wink") # is possible
notify_send(i="face-wink", "title", "subtitle") # will give an error
```
 - You tell me, open a bug if you would like me to add something
