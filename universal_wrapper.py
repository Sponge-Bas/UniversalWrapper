import subprocess

class UniversalWrapper():
    def __init__(self, cmd, divider=' '):
        self.cmd = cmd
        self.divider = divider

    def run_cmd(self, command):
        return subprocess.check_output(command, shell=True).decode('ascii').splitlines()

    def __getattr__(self, name):
        def _wrapped(*args, **kwargs):
            output = self.cmd+' '+name.replace('_',self.divider)+' '
            for string in args:
                output += str(string)+' '
            for key, value in kwargs.items():
                if key == 'root' and value == True:
                    output = 'sudo '+output
                    continue
                output += '--'+str(key)+' '
                if not value == True:
                    output += str(value)+' '
            output = self.run_cmd(output)
            return output
        return _wrapped
