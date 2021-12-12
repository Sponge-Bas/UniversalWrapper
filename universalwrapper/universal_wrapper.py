# Copyright 2021 by Bas de Bruijne
# All rights reserved.
# Universal Wrapper comes with ABSOLUTELY NO WARRANTY, the writer can not be
# held responsible for any problems caused by the use of this script.

import subprocess
import json
import yaml
import sys
from copy import copy


class UWSettings:
    __freeze = False

    def __init__(self):
        """Loads default uw settings"""
        self.cmd = ""
        self.divider = "-"
        self.class_divider = " "
        self.flag_divider = "-"
        self.input_add = {}
        self.input_move = {}
        self.input_custom = []
        self.output_decode = True
        self.output_yaml = False
        self.output_json = False
        self.output_splitlines = False
        self.output_custom = []
        self.debug = False
        self.__freeze = True

    def __setattr__(self, key, value):
        """Prevents the creating of misspelled uw_settings"""
        if self.__freeze and not hasattr(self, key):
            functions = [item for item in dir(self) if not item.startswith("_")]
            raise ImportError(f"Valid settings are limited to {functions}")
        object.__setattr__(self, key, value)


class UniversalWrapper:
    def __init__(self, cmd, uw_settings=None, **kwargs):
        """Loads the default settings and changes the settings if requested"""
        if uw_settings:
            self.uw_settings = uw_settings
        else:
            self.uw_settings = UWSettings()
            for key, value in kwargs.items():
                setattr(self.uw_settings, key, value)
        self.uw_settings.cmd = cmd.replace("_", self.uw_settings.divider).split(" ")
        self._flags_to_remove = []

    def __call__(self, *args, **kwargs):
        """Receives the users commands and directs them to the right defs"""
        command = self.uw_settings.cmd[:]
        command.extend(self._generate_command(*args, **kwargs))
        command = self._input_modifier(command)
        if self._root:
            command = ["sudo"] + command
        return self._run_cmd(command)

    def _generate_command(self, *args, **kwargs):
        """Transforms the args and kwargs to bash arguments and flags"""
        command = []
        self._root = False
        for string in args:
            command.append(str(string))
        for key, values in kwargs.items():
            if key == "root" and values is True:
                self._root = True
            elif values is False:
                self._flags_to_remove.append(self._add_dashes(key))
            else:
                if type(values) != list:
                    values = [values]
                for value in values:
                    command.append(self._add_dashes(key))
                    command[-1] += (" " + str(value)) * (not value is True)
        return command

    def _add_dashes(self, flag):
        """Adds the right number of dashes for the bash flags"""
        if len(str(flag)) > 1:
            return "--" + str(flag.replace("_", self.uw_settings.flag_divider))
        else:
            return "-" + str(flag)

    def _input_modifier(self, command):
        """Handles the input modifiers, e.g. adding and moving commands"""
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

    def _insert_command(self, command, input_command, index):
        """Combines list.append and list.inset to a continues insert function"""
        if index == -1:
            command.append(input_command)
            return command
        elif index < 0:
            index += 1
        command.insert(index, input_command)
        return command

    def _run_cmd(self, command):
        """Forwards the genetared command to subprocess, or prints output if debug"""
        cmd = " ".join([cmd.strip() for cmd in command if cmd]).strip()
        if self.uw_settings.debug:
            print("Generated command:")
            print(cmd)
        else:
            output = subprocess.check_output(cmd, shell=True)
            return self._output_modifier(output)

    def _output_modifier(self, output):
        """Modifies the subprocess' output according to uw_settings"""
        if self.uw_settings.output_decode:
            output = output.decode("ascii")
        if self.uw_settings.output_yaml:
            try:
                output = yaml.safe_load(output)
            except Exception as e:
                print("Parse yaml failed")
                print(e)
        if self.uw_settings.output_json:
            try:
                output = json.loads(output)
            except Exception as e:
                print("Parse json failed")
                print(e)
        if self.uw_settings.output_splitlines:
            output = output.splitlines()
        for cmd in self.uw_settings.output_custom:
            exec(cmd)
        return output

    def __getattr__(self, attr):
        """Handles the creation of (sub)classes"""
        subclass = UniversalWrapper(
            " ".join(self.uw_settings.cmd)
            + self.uw_settings.class_divider
            + attr.replace("_", self.uw_settings.divider),
            uw_settings=copy(self.uw_settings),
        )
        return subclass


def __getattr__(attr):
    """Redirects all trafic to UniversalWrapper"""
    return UniversalWrapper(attr)
