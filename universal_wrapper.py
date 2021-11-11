import subprocess


class UniversalWrapper:
    def __init__(self, cmd, divider=" ", class_divider=None):
        self.cmd = cmd
        self.divider = divider
        if class_divider is None:
            self.class_divider = divider
        else:
            self.class_divider = class_divider

    def run_cmd(self, command):
        print(command)
        print("--")
        command = self.input_modifier(command)
        output = subprocess.check_output(command, shell=True)
        return self.output_modifier(output)

    def __call__(self, *args, **kwargs):
        command = self.cmd + " " + self.generate_command(*args, **kwargs)
        return self.run_cmd(command)

    def input_modifier(self, command):
        return command

    def output_modifier(self, output):
        return output.decode("ascii").splitlines()

    def generate_command(self, *args, **kwargs):
        command = ""
        for string in args:
            command += str(string) + " "
        for key, value in kwargs.items():
            if key == "root" and value == True:
                command = "sudo " + command
                continue
            if len(str(key)) > 1:
                command += "--" + str(key.replace("_", self.divider)) + " "
            else:
                command += "-" + str(key) + " "
            if not value == True:
                command += str(value) + " "
        return command

    def __getattr__(self, attr):
        subclass = UniversalWrapper(
            self.cmd + self.class_divider + attr.replace("_", self.divider),
            self.divider,
            self.class_divider,
        )
        return subclass
