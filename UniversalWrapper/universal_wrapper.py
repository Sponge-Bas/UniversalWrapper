# Copyright 2021 by Bas de Bruijne
# All rights reserved.
# Universal Wrapper comes with ABSOLUTELY NO WARRANTY, the writer can not be
# held responsible for any problems caused by the use of this script.

import subprocess


class UniversalWrapper:
    def __init__(self, cmd, divider=" ", class_divider=" "):
        self.cmd = cmd
        self.divider = divider
        self.class_divider = class_divider
        self.flags_to_remove = []

    def run_cmd(self, command):
        command = self.input_modifier(command)
        command = self.remove_flags(command)
        output = subprocess.check_output(command, shell=True)
        return self.output_modifier(output)

    def __call__(self, *args, **kwargs):
        command = self.cmd + " " + self.generate_command(*args, **kwargs)
        return self.run_cmd(command)

    def input_modifier(self, command):
        return command

    def output_modifier(self, output):
        return output.decode("ascii")

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
            return "--" + str(flag.replace("_", self.divider)) + " "
        else:
            return "-" + str(flag) + " "

    def __getattr__(self, attr):
        subclass = UniversalWrapper(
            self.cmd + self.class_divider + attr.replace("_", self.divider),
            self.divider,
            self.class_divider,
        )
        return subclass
