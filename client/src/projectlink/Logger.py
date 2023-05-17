from .imports import *

class Logger:
    def __init__(self, prefix, debug=False):
        self.prefix = prefix
        self.debug = debug

    def log(self, arg, prefix="", *args):
        prefix = f"[{colored(self.prefix, 'blue') + colored('::' + prefix, 'white') if prefix else ''}]"
        out = f"{prefix} {arg} "
        for arg in args:
            out += f"{arg} "
        print(out)
    
    def error(self, arg, prefix="", *args):
        prefix = f"[{colored(self.prefix, 'red') + colored('::' + prefix, 'white') if prefix else ''}]"
        out = f"{prefix} {arg} "
        for arg in args:
            out += f"{arg} "
        print(out)

    def success(self, arg, prefix="", *args):
        prefix = f"[{colored(self.prefix, 'green') + colored('::' + prefix, 'white') if prefix else ''}]"
        out = f"{prefix} {arg} "
        for arg in args:
            out += f"{arg} "
        print(out)

    def warn(self, arg, prefix="", *args):
        prefix = f"[{colored(self.prefix, 'yellow') + colored('::' + prefix, 'white') if prefix else ''}]"
        out = f"{prefix} {arg} "
        for arg in args:
            out += f"{arg} "
        print(out)

    def debug(self, arg, prefix="", *args):
        if self.debug:
            prefix = f"[{colored(self.prefix, 'magenta') + colored('::' + prefix, 'white') if prefix else ''}]"
            out = f"{prefix} {arg} "
            for arg in args:
                out += f"{arg} "
            print(out)
