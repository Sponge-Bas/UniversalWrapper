# Copyright 2021 by Bas de Bruijne
# All rights reserved.
# Universal Wrapper comes with ABSOLUTELY NO WARRANTY, the writer can not be
# held responsible for any problems caused by the use of this script.

import subprocess
import json
import yaml
import sys
from copy import copy


class UniversalWrapper:
    def __init__(
        self,
        cmd,
        divider="-",
        class_divider=" ",
        flag_divider="-",
        input_modifiers={"add": {}, "move": {}, "custom": []},
        output_modifiers={
            "decode": True,
            "split_lines": False,
            "parse_yaml": False,
            "parse_json": False,
            "custom": [],
        },
        uw_settings=None,
    ):
        if uw_settings is None:
            self.uw_settings = {}
            self.uw_settings["cmd"] = cmd
            self.uw_settings["divider"] = divider
            self.uw_settings["class_divider"] = class_divider
            self.uw_settings["flag_divider"] = flag_divider
            self.uw_settings["input_modifiers"] = input_modifiers
            self.uw_settings["output_modifiers"] = output_modifiers
            self.uw_settings["debug"] = False
        else:
            self.uw_settings = uw_settings
            self.uw_settings["cmd"] = cmd
        self._flags_to_remove = []

    def _run_cmd(self, command):
        command = self._input_modifier(command)
        command = self._remove_flags(command)
        if self.uw_settings["debug"]:
            print("Generated command:")
            print(command)
        else:
            output = subprocess.check_output(command.strip(), shell=True)
        return self._output_modifier(output)

    def __call__(self, *args, **kwargs):
        command = (
            self.uw_settings["cmd"].replace("_", self.uw_settings["divider"])
            + " "
            + self._generate_command(*args, **kwargs)
        )
        return self._run_cmd(command)

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
        for modifier, action in self.uw_settings["input_modifiers"].items():
            if modifier == "add" or modifier == "move":
                for input_command, index in action.items():
                    extra_flag = ""
                    if modifier == "move":
                        if input_command in command:
                            command_index = command.index(input_command)
                            command.pop(command_index)
                            if input_command.startswith("-") and not command[
                                command_index
                            ].startswith("-"):
                                extra_flag = " " + command[command_index]
                                command.pop(command_index)
                        else:
                            continue
                    command = self._inset_command(
                        command, input_command + extra_flag, index
                    )
            elif modifier == "custom":
                for cmd in action:
                    exec(cmd)
        command = " ".join(command)
        if command[0] == " ":
            command = command[1:]
        return command

    def _output_modifier(self, output):
        for key, value in self.uw_settings["output_modifiers"].items():
            if key == "custom":
                for command in value:
                    exec(command)
            if not value is True:
                continue
            elif key == "decode":
                output = output.decode("ascii")
            elif key == "split_lines":
                output = output.splitlines()
            elif key == "parse_json":
                try:
                    output = json.loads(output)
                except Exception as e:
                    print("Parse json failed")
                    print(e)
            elif key == "parse_yaml":
                try:
                    output = yaml.safe_load(output)
                except Exception as e:
                    print("Parse yaml failed")
                    print(e)

        return output

    def _generate_command(self, *args, **kwargs):
        command = ""
        for string in args:
            command += str(string) + " "
        for key, value in kwargs.items():
            if key == "root" and value is True:
                command = "sudo " + command
            elif value is False:
                self._flags_to_remove.append(self._add_dashes(key))
            else:
                for value in self._to_list(value):
                    command += self._add_dashes(key)
                    command += (str(value) + " ") * (not value is True)
        return command

    def _remove_flags(self, command):
        input_modifiers = list(self.uw_settings["input_modifiers"]["add"].keys())
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
            return "--" + str(flag.replace("_", self.uw_settings["flag_divider"])) + " "
        else:
            return "-" + str(flag) + " "

    def __getattr__(self, attr):
        subclass = UniversalWrapper(
            self.uw_settings["cmd"]
            + self.uw_settings["class_divider"]
            + attr.replace("_", self.uw_settings["divider"]),
            uw_settings=copy(self.uw_settings),
        )
        return subclass


def __getattr__(attr):
    return UniversalWrapper(attr)
