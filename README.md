# UniversalWrapper
Use any shell command in python conveniently.

Based on subprocess, the universal wrapper provides an intuitive wrapper around any cli.
Only tested on ubuntu.

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
git.diff(name_only=True)
```

