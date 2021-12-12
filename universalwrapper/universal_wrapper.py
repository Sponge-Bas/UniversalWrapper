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
        if self.__freeze and not hasattr(self, key):
            raise ImportError(
                f"Valid settings are limited to {[item for item in dir(self) if not item.startswith('_')]}"
            )
        object.__setattr__(self, key, value)


class UniversalWrapper:
    def __init__(
        self,
        cmd,
        uw_settings=None,
        **kwargs,
    ):
        if uw_settings is None:
            self.uw_settings = UWSettings()
            for key, value in kwargs.items():
                setattr(self.uw_settings, key, value)
        else:
            self.uw_settings = uw_settings
        self.uw_settings.cmd = cmd
        self._flags_to_remove = []

    def _run_cmd(self, command):
        command = self._input_modifier(command)
        command = self._remove_flags(command)
        if self.uw_settings.debug:
            print("Generated command:")
            print(command)
        else:
            output = subprocess.check_output(command.strip(), shell=True)
            return self._output_modifier(output)

    def __call__(self, *args, **kwargs):
        command = (
            self.uw_settings.cmd.replace("_", self.uw_settings.divider)
            + " "
            + self._generate_command(*args, **kwargs)
        )
        return self._run_cmd("sudo " * self._root + command)

    def _inset_command(self, command, input_command, index):
        if index == -1:
            command.append(input_command)
            return command
        elif index < 0:
            index += 1
        command.insert(index, input_command)
        return command

    def _input_modifier(self, command):
        command = command.split(" ")
        for input_command, index in self.uw_settings.input_add.items():
            command = self._inset_command(command, input_command, index)
        for input_command, index in self.uw_settings.input_move.items():
            extra_flag = ""
            if input_command in command:
                command_index = command.index(input_command)
                command.pop(command_index)
                if input_command.startswith("-") and not command[
                    command_index
                ].startswith("-"):
                    extra_flag = " " + command[command_index]
                    command.pop(command_index)
                command = self._inset_command(
                    command, input_command + extra_flag, index
                )
        for cmd in self.uw_settings.input_custom:
            exec(cmd)
        command = " ".join(command)
        if command[0] == " ":
            command = command[1:]
        return command

    def _output_modifier(self, output):
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

    def _generate_command(self, *args, **kwargs):
        command = ""
        self._root = False
        for string in args:
            command += str(string) + " "
        for key, value in kwargs.items():
            if key == "root" and value is True:
                self._root = True
            elif value is False:
                self._flags_to_remove.append(self._add_dashes(key))
            else:
                for value in self._to_list(value):
                    command += self._add_dashes(key)
                    command += (str(value) + " ") * (not value is True)
        return command

    def _remove_flags(self, command):
        input_modifiers = list(self.uw_settings.input_add.keys())
        for flag in self._flags_to_remove:
            for input_modifier in input_modifiers:
                if flag.strip() in input_modifier:
                    command = command.replace(input_modifier, "")
        self._flags_to_remove = []
        return command

    def _to_list(self, values):
        if type(values) != list:
            values = [values]
        return values

    def _add_dashes(self, flag):
        if len(str(flag)) > 1:
            return "--" + str(flag.replace("_", self.uw_settings.flag_divider)) + " "
        else:
            return "-" + str(flag) + " "

    def __getattr__(self, attr):
        subclass = UniversalWrapper(
            self.uw_settings.cmd
            + self.uw_settings.class_divider
            + attr.replace("_", self.uw_settings.divider),
            uw_settings=copy(self.uw_settings),
        )
        return subclass


def __getattr__(attr):
    return UniversalWrapper(attr)
