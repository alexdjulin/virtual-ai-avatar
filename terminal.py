# Define terminal codes to import and use in print statements
# Example: print(f"{RED}This is red text{RESET}")

from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Regular text colors
BLACK = Fore.BLACK
RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
PURPLE = Fore.MAGENTA
CYAN = Fore.CYAN
WHITE = Fore.WHITE
GREY = Fore.BLACK + Style.BRIGHT  # Bright black for grey

# Bold text colors
BOLD_BLACK = Style.BRIGHT + Fore.BLACK
BOLD_RED = Style.BRIGHT + Fore.RED
BOLD_GREEN = Style.BRIGHT + Fore.GREEN
BOLD_YELLOW = Style.BRIGHT + Fore.YELLOW
BOLD_BLUE = Style.BRIGHT + Fore.BLUE
BOLD_PURPLE = Style.BRIGHT + Fore.MAGENTA
BOLD_CYAN = Style.BRIGHT + Fore.CYAN
BOLD_WHITE = Style.BRIGHT + Fore.WHITE

# Background colors
BG_BLACK = Fore.BLACK + Style.BRIGHT
BG_RED = Fore.RED + Style.BRIGHT
BG_GREEN = Fore.GREEN + Style.BRIGHT
BG_YELLOW = Fore.YELLOW + Style.BRIGHT
BG_BLUE = Fore.BLUE + Style.BRIGHT
BG_PURPLE = Fore.MAGENTA + Style.BRIGHT
BG_CYAN = Fore.CYAN + Style.BRIGHT
BG_WHITE = Fore.WHITE + Style.BRIGHT

# Reset formatting
RESET = Style.RESET_ALL

# Clear line (override with 50 blank spaces) and go back to line start
CLEAR = f'\r{50*" "}\r'
