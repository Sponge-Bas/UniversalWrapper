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
        input_modifiers={},
        output_modifiers={
            "decode": True,
            "split_lines": False,
            "parse_yaml": False,
            "parse_json": False,
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
        self.flags_to_remove = []

    def run_cmd(self, command):
        command = self.input_modifier(command)
        command = self.remove_flags(command)
        if self.uw_settings["debug"]:
            print("Executing")
            print(command)
            print(">>")
        output = subprocess.check_output(command, shell=True)
        return self.output_modifier(output)

    def __call__(self, *args, **kwargs):
        command = (
            self.uw_settings["cmd"].replace("_", self.uw_settings["divider"])
            + " "
            + self.generate_command(*args, **kwargs)
        )
        return self.run_cmd(command)

    def input_modifier(self, command):
        command = command.split(" ")
        for input_command, index in self.uw_settings["input_modifiers"].items():
            if index == -1:
                command.append(input_command)
                continue
            elif index < 0:
                index += 1
            command.insert(index, input_command)
        command = " ".join(command)
        if command[0] == " ":
            command = command[1:]
        return command

    def output_modifier(self, output):
        if self.uw_settings["output_modifiers"]["decode"]:
            output = output.decode("ascii")
        if self.uw_settings["output_modifiers"]["split_lines"]:
            output = output.splitlines()
        if self.uw_settings["output_modifiers"]["parse_json"]:
            try:
                output = json.loads(output)
            except:
                print("Parse json failed")
        if self.uw_settings["output_modifiers"]["parse_yaml"]:
            try:
                output = yaml.load(output)
            except:
                print("Parse yaml failed")
        return output

    def generate_command(self, *args, **kwargs):
        command = ""
        for string in args:
            command += str(string) + " "
        for key, value in kwargs.items():
            if key == "root" and value is True:
                command = "sudo " + command
            elif value is False:
                self.flags_to_remove.append(self.add_dashes(key))
            else:
                for value in self.to_list(value):
                    command += self.add_dashes(key)
                    command += (str(value) + " ") * (not value is True)
        return command

    def remove_flags(self, command):
        input_modifiers = self.uw_settings["input_modifiers"].keys()
        for flag in self.flags_to_remove:
            for input_modifier in input_modifiers:
                if flag in input_modifier:
                    command = command.replace(input_modifier, "")
        self.flags_to_remove = []
        return command

    def to_list(self, values):
        if type(values) != list:
            values = [values]
        return values

    def add_dashes(self, flag):
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
