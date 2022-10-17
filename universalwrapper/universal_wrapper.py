# Copyright 2022 by Bas de Bruijne
# All rights reserved.
# Universal Wrapper comes with ABSOLUTELY NO WARRANTY, the writer can not be
# held responsible for any problems caused by the use of this module.

import asyncio
import json
import logging
import shlex
import subprocess
import yaml

from copy import copy
from typing import Union, List, Dict


class UWSettings:
    __freeze = False

    def __init__(self) -> None:
        """Loads default uw settings"""
        self.cmd: str = ""  # Base command
        self.divider: str = "-"  # String to replace "_" with in commands
        self.class_divider: str = " "  # String to place in between classes
        self.flag_divider: str = "-"  # String to replace "_" with in flags
        self.input_add: Dict[str:int] = {}  # {extra command, index where to add it}
        self.input_move: Dict[str:int] = {}  # {extra command, index where to move it}
        self.input_custom: List[str] = []  # custom command: e.g. "command.reverse()"
        self.output_decode: bool = True  # Decode output to str
        self.output_yaml: bool = False  # Parse yaml from output
        self.output_json: bool = False  # Parse json from output
        self.output_splitlines: bool = False  # Split lines of output
        self.output_custom: List[str] = []  # custom command: e.g. "output.reverse()"
        self.debug: bool = False  # Don't run commands but instead print the command
        self.enable_async: bool = False  # Globally enable asyncio
        self.double_dash: bool = True  # Use -- instead of - for multi-character flags

        self.cmd_chain: List[str] = []
        self.__freeze: bool = True

    def __setattr__(self, key: str, value: object) -> None:
        """Prevents the creating of misspelled uw_settings

        :param key: uw_settings key to change
        :param value: value to change key to
        """
        if self.__freeze and not hasattr(self, key):
            functions = [item for item in dir(self) if not item.startswith("_")]
            raise ImportError(f"Valid settings are limited to {functions}")
        if key == "divider" and hasattr(self, key):
            self._reset_command(value)
        object.__setattr__(self, key, value)

    def _reset_command(self, divider: str = None) -> None:
        """Resets cmd_chain to its original value

        When a command is chained, its chain history is stored in cmd_chain. After that
        command has been called the chain needs to be reset to the original command.
        :param divider: The new divider, only applicable if the divider has changed
        """
        if divider:
            self.cmd = self.cmd.replace(self.divider, divider)
        self.cmd_chain = self.cmd.split(" ")

    def _update_command(self, value: str) -> None:
        """Add new value to the cmd_chain

        :param value: value to add to the cmd_chain
        """
        self.cmd_chain = (
            (
                f"{' '.join(self.cmd_chain)}{self.class_divider}"
                f"{value.replace('_', self.divider)}"
            )
            .replace("_", self.divider)
            .split(" ")
        )


class UniversalWrapper:
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
        command = self.uw_settings.cmd_chain[:]
        self.uw_settings._reset_command()
        command = self._check_async(command)
        command.extend(self._generate_command(*args, **kwargs))
        command = self._input_modifier(command)
        if self._root:
            command = ["sudo"] + command
        cmd = shlex.split(" ".join(command))
        if self.uw_settings.debug:
            print(f"Generated command:\n{cmd}")
            return
        logging.debug("Calling shell command '{cmd}'")
        if self._enable_async:
            return self._async_run_cmd(cmd)
        else:
            return self._run_cmd(cmd)

    def _check_async(self, command: List[str]) -> List[str]:
        """Checks the command for the "async_" keyword

        :param command: Initial command with possible "async_" keyword
        :returns: command with keyword removed. Async enablement is stored in
        self._enable_async
        """
        self._enable_async = self.uw_settings.enable_async
        for i, cmd in enumerate(command):
            if cmd.startswith(f"async{self.uw_settings.divider}"):
                logging.debug("Async keyword found")
                command[i] = cmd.replace(f"async{self.uw_settings.divider}", "")
                self._enable_async = True
        return command

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
            if key == "root" and values is True:
                self._root = True
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
        if len(str(flag)) > 1 and self.uw_settings.double_dash:
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
        """Forwards the generated command to subprocess and handles
        error displaying

        :param: List of string which combined make the shell command
        :returns: Output of shell command
        """
        try:
            output = subprocess.check_output(cmd)
        except subprocess.CalledProcessError as e:
            print(e.output.decode())
            raise
        return self._output_modifier(output)

    async def _async_run_cmd(self, cmd: List[str]) -> str:
        """Forwards the generated command to async subprocess and
        handles error displaying

        :param: List of string which combined make the shell command
        :returns: Output of shell command
        """
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        async def _output(proc):
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                return self._output_modifier(stdout)
            print(stderr.decode())
            raise subprocess.CalledProcessError(proc.returncode, cmd, stdout, stderr)

        return _output(proc)

    def _output_modifier(self, output: str) -> str:
        """Modifies the subprocess' output according to uw_settings

        :param output: string to modify, e.g. parse
        :returns: modified output
        """
        if self.uw_settings.output_decode:
            output = output.decode()
        if self.uw_settings.output_yaml:
            try:
                output = yaml.safe_load(output)
            except Exception as e:
                logging.warning("Parse yaml failed")
                logging.warning(e)
        if self.uw_settings.output_json:
            try:
                output = json.loads(output)
            except Exception as e:
                logging.warning("Parse json failed")
                logging.warning(e)
        if self.uw_settings.output_splitlines:
            output = output.splitlines()
        for cmd in self.uw_settings.output_custom:
            exec(cmd)
        return output

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
