import sys

braille_symbols = [
    "\033[38;5;40m⠋\033[0m",
    "\033[38;5;40m⠙\033[0m",
    "\033[38;5;40m⠹\033[0m",
    "\033[38;5;40m⠼\033[0m",
    "\033[38;5;40m⠴\033[0m",
    "\033[38;5;40m⠤\033[0m",
    "\033[38;5;40m⠣\033[0m",
    "\033[38;5;40m⠱\033[0m",
]

GREEN_CHECKMARK = "\033[38;5;40m✔\033[0m"  # Green checkmark
RED_CROSS = "\033[38;5;196m✗\033[0m"  # Red cross for failure


class Spinner:
    def __init__(self, message: str = None):
        self.message = message
        self.stop_spinner = False
        self.idx = 0

    def reset(self):
        self.idx = 0

    def start(self):
        self.reset()
        self.spin()

    def spin(self):
        sys.stdout.write(
            f"\r{braille_symbols[self.idx % len(braille_symbols)]} {self.message}"
        )
        sys.stdout.flush()
        self.idx += 1

    def finish(self):
        """
        Make it green
        """
        sys.stdout.write(f"\r{GREEN_CHECKMARK} {self.message}\n")
        sys.stdout.flush()
        self.reset()

    def fail(self):
        """
        Make it red
        """
        sys.stdout.write(f"\r{RED_CROSS} {self.message}\n")
        sys.stdout.flush()
