import subprocess
import importlib.util

class LibManager:
    def __init__(self, 
                 libs: tuple,
                 prefix: str = "python -m pip install ",
                 extra_cmds: tuple = (),
                 instant = False,
                 super = False):

        self.super = " --user" if super else ""
        self.prefix = prefix
        self.libs = libs
        self.extra_cmds = extra_cmds

        if instant:
            self.run()

    def run(self):
        for lib in self.libs:
            lib, identifier = (lib, lib) if isinstance(lib, str) else lib
            if not self._is_installed(identifier):
                print(f"`{lib}` package is missing, proceeding to auto-install")
                self.__install(lib)
        
        for cmd in self.extra_cmds:
            self.__pipethrough(cmd)

    def __install(self, lib):
        subprocess.run(self.prefix + lib + self.super, shell=True)

    def __pipethrough(self, cmd):
        subprocess.run(cmd, shell=True)

    def _is_installed(self, package_name):
        spec = importlib.util.find_spec(package_name)
        if len(package_name.split())-1:
            return True
        return spec is not None
