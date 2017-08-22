import os

class Bcolors():
    CYAN = ''
    GREEN = ''
    YELLOW = ''
    RED = ''
    ENDC = ''

    def __init__(self):
        """
        Set colors based upon
        OS being posix or not.
        """
        if self.check_os() == "posix":
            self.CYAN = '\033[96m'
            self.GREEN = '\033[92m'
            self.YELLOW = '\033[93m'
            self.RED = '\033[91m'
            self.ENDC = '\033[0m'

    def disable(self):
        """
        Reset colors
        """
        self.CYAN = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.RED = ''
        self.ENDC = ''

    def check_os(self):
        """
        Check opertation system
        type
        """
        if os.name == "nt":
            operating_system = "windows"
        if os.name == "posix":
            operating_system = "posix"
        return operating_system
