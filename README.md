# UniversalWrapper
Use any shell command in python conveniently.

Based on subprocess, the universal wrapper provides an intuitive wrapper around any cli.
Tested on ubuntu only. The development is inspired by my jealousy toward bash scripts, where command line tools can be integrated seamlessly into the code. This tool provides a similar level of integration, without having to manually write wappers for the specific cli's. 

Example: create and delete lxd containers

```python
from universal_wrapper import UniversalWrapper as uw

lxc = uw('lxc')
lxc.launch("ubuntu:20.04", "testcontainer")

lxc.delete("testcontainer", force=True)
```

Example: clone a library

```python
git = uw('git', divider='-')
git.clone("https://github.com/Basdbruijne/UniversalWrapper.git")
```
check git diff files:
```python
diff = git.diff(name_only=True)
```
Here, the divider specifies how different cli's define between words. E.g. for `git`, the command `name_only` will transform to `name-only`. By default `divider=" "`. Camel case is not yet supported.

Example: send a notification

```python
notify_send=uw('notify-send')
notify_send("title", "subtitle", i="face-wink")
```

The argument `(root=True)` will trigger `sudo ` in the command.


Limitations:
 - positional argument cannot follow keyword argument, for example:
```python
notify_send("title", "subtitle", i="face-wink") # is possible
notify_send(i="face-wink", "title", "subtitle") # will give an error
```
 - You tell me, open a bug if you would like me to add something
