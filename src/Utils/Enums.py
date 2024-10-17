from enum import Enum
from colorama import Fore

class SystemMode(Enum):
    FILE = 'file'

class StatusType(Enum):
    BOOL = 'bool'
    ENUM = 'enum'

class Color(Enum):
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE

