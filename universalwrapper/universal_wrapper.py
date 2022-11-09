# Copyright 2022 by Bas de Bruijne
# All rights reserved.
# Universal Wrapper comes with ABSOLUTELY NO WARRANTY, the writer can not be
# held responsible for any problems caused by the use of this module.

import asyncio
import json
import shlex
import subprocess
import yaml
import warnings

from typing import ByteString, Union, List, Dict, Any


class UWSettings:
    """This class provides variable tracking for the UniversalWrapper class. These
    variables define the behavior in which the wrapper converts calls to subprocess
    commands.
    """

    _freeze = False

    def __init__(self) -> None:
        """Loads default uw settings"""

        # Global settings
        self.cmd: str = ""  # Base command
        self.divider: str = "-"  # String to replace "_" with in commands
        self.class_divider: str = " "  # String to place in between classes
        self.flag_divider: str = "-"  # String to replace "_" with in flags
        self.input_add: Dict[str:int] = {}  # {extra command, index where to add it}
        self.input_move: Dict[str:int] = {}  # {extra command, index where to move it}
        self.input_custom: List[str] = []  # custom command: e.g. "command.reverse()"
        self.output_custom: List[str] = []  # custom command: e.g. "output.reverse()"

        self._incidentals = []
        # Local or global settings
        self.root: bool = False  # Run commands as sudo, same as `input_add={0: "sudo"}`
        self.debug: bool = False  # Don't run commands but instead print the command
        self.double_dash: bool = True  # Use -- instead of - for multi-character flags
        self.output_yaml: bool = False  # Parse yaml from output
        self.output_json: bool = False  # Parse json from output
        self.enable_async: bool = False  # Globally enable asyncio
        self.return_stderr: bool = False  # Forward stderr output to the return values
        self.output_splitlines: bool = False  # Split lines of output
        self.output_decode: bool = True  # Decode output to str
        self.warn_stderr: bool = True  # Forward stderr output to warnings
        self.cwd: str = None  # Current working directory
        self.env: str = None  # Env for environment variables

        self._cmd_chain: List[str] = []
        self._freeze: bool = True

    def __setattr__(self, key: str, value: object) -> None:
        """Prevents the creating of misspelled uw_settings

        :param key: uw_settings key to change
        :param value: value to change key to
        """
        if self._freeze and not hasattr(self, key):
            functions = [item for item in dir(self) if not item.startswith("_")]
            raise ImportError(f"Valid settings are limited to {functions}")
        if (
            not self._freeze
            and hasattr(self, "_incidentals")
            and not key.startswith("_")
        ):
            self._incidentals.append(key)
        if key == "divider" and hasattr(self, key):
            self._reset_command(value)
        object.__setattr__(self, key, value)
        if self._freeze and key == "cmd":
            self._reset_command()

    def _reset_command(self, divider: str = None) -> None:
        """Resets cmd_chain to its original value

        When a command is chained, its chain history is stored in cmd_chain. After that
        command has been called the chain needs to be reset to the original command.
        :param divider: The new divider, only applicable if the divider has changed
        """
        if divider:
            self.cmd = self.cmd.replace(self.divider, divider)
        self._freeze = False
        self._cmd_chain = self.cmd.split(" ")
        self._freeze = True

    def _update_command(self, value: str) -> None:
        """Add new value to the cmd_chain

        :param value: value to add to the cmd_chain
        """
        self._freeze = False
        self._cmd_chain = (
            (
                f"{' '.join(self._cmd_chain)}{self.class_divider}"
                f"{value.replace('_', self.divider)}"
            )
            .replace("_", self.divider)
            .split(" ")
        )
        self._freeze = True


class SubprocessError(subprocess.CalledProcessError):
    """Error class derived from subprocess.CalledProcessError to make the error message
    more intuitive by including the commands output
    """

    def __str__(self) -> str:
        """Compiles variables from self to a coherent error message

        :returns: Error message
        """
        msg = f"{super().__str__()[:-1]}:\n"
        for err in ("stdout", "stderr"):
            std = getattr(self, err)
            if std:
                std = std.decode().strip().replace("\n", "\n| ")
                msg += f"{err}:\n| {std}\n"
        return msg


class UniversalWrapper:
    """UniversalWrapper is a convenient shell wrapper for python, allowing you to
    interact with command line interfaces as if they were Python modules.
    UniversalWrapper has no code specific to any particular command and the use of
    UniversalWrapper is in no way limited to the commands below.

    Example usage:
      ```
      from universalwrapper import git

      git.clone("https://github.com/Basdbruijne/UniversalWrapper.git")
      diff = git.diff(name_only=True)
      ```

    To adjust the behavior of the wrapper, the uw_settings attribute of the wrapper can
    be adjusted according to the rules defined under `class UwSettings`.
    """

    def __init__(self, cmd: str, uw_settings: UWSettings = None, **kwargs) -> None:
        """Loads the default settings and changes the settings if requested

        :param cmd: Base command for the class
        :uw_settings: Pre-configured UWSettings object
        :kwargs: {key: value} UWSettings to configure
        """
        if uw_settings:
            self.uw_settings = uw_settings
        else:
            self.uw_settings = UWSettings()
            for key, value in kwargs.items():
                setattr(self.uw_settings, key, value)
        self.uw_settings.cmd = cmd.replace("_", self.uw_settings.divider)
        self.uw_settings._reset_command()
        self._flags_to_remove = []

    def __call__(self, *args: Union[int, str], **kwargs: Union[int, str]) -> str:
        """Receives the users commands and directs them to the right functions

        :param args: collection of non-keyword arguments for the shell call
        :param kwargs: collection of keyword arguments for the shell call, can
        either be `key = value` for `--key value` or `key = True` for `--key`
        :returns: Response of the shell call
        """
        command = self.uw_settings._cmd_chain[:]
        self.uw_settings._reset_command()
        for key in self.uw_settings._incidentals:
            setattr(self, f"_{key}", getattr(self.uw_settings, key))
        command.extend(self._generate_command(*args, **kwargs))
        command = self._input_modifier(command)
        if self._root:
            command = ["sudo"] + command
        cmd = shlex.split(" ".join(command), posix=False)
        if self._debug:
            print(f"Generated command:\n{cmd}")
            return
        if self._enable_async:
            return self._async_run_cmd(cmd)
        else:
            return self._run_cmd(cmd)

    def _generate_command(
        self, *args: Union[int, str], **kwargs: Union[int, str]
    ) -> List[str]:
        """Transforms the args and kwargs to bash arguments and flags

        :param args: collection of non-keyword arguments for the shell call
        :param kwargs: collection of keyword arguments for the shell call
        :returns: Shell call
        """
        command = []
        self._root = False
        for string in args:
            if " " in str(string):
                string = f"'{string}'"
            command.append(str(string))
        for key, values in kwargs.items():
            if key.startswith("_") and key[1:] in self.uw_settings._incidentals:
                setattr(self, key, values)
            else:
                if type(values) != list:
                    values = [values]
                for value in values:
                    if value is False:
                        self._flags_to_remove.append(self._add_dashes(key))
                    else:
                        command.append(self._add_dashes(key))
                        command[-1] += f" {value}" * (not value is True)
        return command

    def _add_dashes(self, flag: str) -> str:
        """Adds the right number of dashes for the bash flags based on the
        convention that single lettered flags get a single dash and multi-
        lettered flags get a double dash

        :param flag: flag to add dashes to
        :returns: flag with dashes
        """
        if len(str(flag)) > 1 and self._double_dash:
            return f"--{flag.replace('_', self.uw_settings.flag_divider)}"
        else:
            return f"-{flag}"

    def _input_modifier(self, command: List[str]) -> List[str]:
        """Handles the input modifiers, e.g. adding and moving commands

        :param command: List of initial commands
        :returns: Modified list of commands based on uw_settings input
        modifiers
        """
        for input_command, index in self.uw_settings.input_add.items():
            if not input_command.split(" ")[0] in self._flags_to_remove:
                command = self._insert_command(command, input_command, index)
        self._flags_to_remove = []
        for move_command, index in self.uw_settings.input_move.items():
            cmd = [cmd.split(" ")[0] for cmd in command]
            if move_command in cmd:
                command_index = cmd.index(move_command)
                popped_command = command.pop(command_index)
                command = self._insert_command(command, popped_command, index)
        for cmd in self.uw_settings.input_custom:
            exec(cmd)
        return command

    def _insert_command(
        self, command: List[str], input_command: str, index: int
    ) -> List[str]:
        """Combines list.append and list.inset to a continues insert function

        :param command: Initial command to add items to
        :param input_command: Item to add to command
        :param index: Index to add command, must be in range(0, len(command))
        or -1
        :returns: Modified command
        """
        if index == -1:
            command.append(input_command)
            return command
        elif index < 0:
            index += 1
        command.insert(index, input_command)
        return command

    def _run_cmd(self, cmd: List[str]) -> str:
        """Forwards the generated command to subprocess

        :param: List of string which combined make the shell command
        :returns: Output of shell command
        """
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self._cwd,
            env=self._env,
        )
        stdout, stderr = proc.communicate()
        return self._raise_or_return(stdout, stderr, proc.returncode, cmd)

    async def _async_run_cmd(self, cmd: List[str]) -> str:
        """Forwards the generated command to async subprocess

        :param: List of string which combined make the shell command
        :returns: Output of shell command
        """
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=self._cwd,
            env=self._env,
        )

        async def _output(proc):
            stdout, stderr = await proc.communicate()
            return self._raise_or_return(stdout, stderr, proc.returncode, cmd)

        return _output(proc)

    def _raise_or_return(
        self, stdout: ByteString, stderr: ByteString, return_code: int, cmd: List[str]
    ) -> str:
        """Handles the error displaying for the subprocesses

        :param stdout: subprocess output
        :param stderr: subprocess error output
        :param return_code: return code of the process
        :param cmd: original command, used for error message
        :returns: Output of shell command
        """
        if return_code == 0:
            if stderr and self._warn_stderr:
                warnings.warn("\n" + stderr.decode(), UserWarning, stacklevel=4)
            if self._return_stderr:
                stdout = stderr + b"\n" + stdout
            return self._output_modifier(stdout)
        raise SubprocessError(return_code, cmd, stdout, stderr)

    def _output_modifier(self, output: str) -> str:
        """Modifies the subprocess' output according to uw_settings

        :param output: string to modify, e.g. parse
        :returns: modified output
        """
        if self._output_decode:
            output = output.decode()
        if self._output_yaml:
            output = yaml.safe_load(output)
        if self._output_json:
            output = json.loads(output)
        if self._output_splitlines:
            output = output.splitlines()
        for cmd in self.uw_settings.output_custom:
            exec(cmd)
        return self._pretty_output(output)

    def _pretty_output(self, output: object) -> object:
        """Makes pretty prints when debugging

        :param output: The output of the cmd command
        :returns: Output with __repr__ set to pretty print when debugging
        """

        class UWOutput(type(output)):
            def __repr__(self):
                if isinstance(self, dict) or isinstance(self, list):
                    return json.dumps(self, indent=2, default=str)
                return self

            def __getattribute__(self, __name: str) -> Any:
                if not hasattr(super(), __name):
                    msg = (
                        f"'{type(output).__name__}' object has no attribute '{__name}'"
                    )
                    raise AttributeError(msg)
                return super().__getattribute__(__name)

        return UWOutput(output)

    def __getattr__(self, attr: str) -> object:
        """Handles the creation of (sub)classes

        :param attr: next section of command to construct
        :returns: universalwrapper class
        """
        self.uw_settings._update_command(attr)
        return self


def __getattr__(attr):
    """Redirects all traffic to UniversalWrapper"""
    return UniversalWrapper(attr)
