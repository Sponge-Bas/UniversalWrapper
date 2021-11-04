import subprocess


class UniversalWrapper:
    def __init__(self, cmd, divider=" "):
        self.cmd = cmd
        self.divider = divider

    def run_cmd(self, command):
        return subprocess.check_output(command, shell=True).decode("ascii").splitlines()

    def __call__(self, *args, **kwargs):
        command = self.cmd + " "
        command += self.generate_command(*args, **kwargs)
        return self.run_cmd(command)

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

    def __getattr__(self, name):
        def _wrapped(*args, **kwargs):
            command = self.cmd + " " + name.replace("_", self.divider) + " "
            command += self.generate_command(*args, **kwargs)
            return self.run_cmd(command)

        return _wrapped
