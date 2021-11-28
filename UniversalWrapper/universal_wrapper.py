# Copyright 2021 by Bas de Bruijne
# All rights reserved.
# Universal Wrapper comes with ABSOLUTELY NO WARRANTY, the writer can not be
# held responsible for any problems caused by the use of this script.

import subprocess
import json
import yaml


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
    ):
        self.uw_settings = {}
        self.uw_settings["cmd"] = cmd
        self.uw_settings["divider"] = divider
        self.uw_settings["class_divider"] = class_divider
        self.uw_settings["flag_divider"] = flag_divider
        self.uw_settings["input_modifiers"] = input_modifiers
        self.uw_settings["output_modifiers"] = output_modifiers
        self.flags_to_remove = []

    def run_cmd(self, command):
        command = self.input_modifier(command)
        command = self.remove_flags(command)
        output = subprocess.check_output(command, shell=True)
        return self.output_modifier(output)

    def __call__(self, *args, **kwargs):
        command = self.uw_settings["cmd"] + " " + self.generate_command(*args, **kwargs)
        return self.run_cmd(command)

    def input_modifier(self, command):
        command = command.split(" ")
        for input_command, index in self.uw_settings["input_modifiers"].items():
            command.insert(index, input_command)
        command = " ".join(command)
        return command

    def output_modifier(self, output):
        if self.uw_settings["output_modifiers"]["decode"]:
            output = output.decode("ascii")
        if self.uw_settings["output_modifiers"]["split_lines"]:
            output = output.splitlines()
        if self.uw_settings["output_modifiers"]["parse_json"]:
            output = json.loads(output)
        if self.uw_settings["output_modifiers"]["parse_yaml"]:
            output = yaml.load(output)
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
        for flag in self.flags_to_remove:
            command = command.replace(flag.strip(), "")
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
            self.uw_settings["divider"],
            self.uw_settings["class_divider"],
        )
        return subclass


def __getattr__(attr):
    return UniversalWrapper(attr)
