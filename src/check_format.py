import re
from .error import FormatError


class CheckFormat():
    def __init__(self):
        self.nb_drones_regex = r"^nb_drones:\s*(\d+)$"

    def is_drones_first_line(self, lines: list[str]):
        self.start = True
        for i, line in enumerate(lines):
            if self.ignore_line(line):
                continue
            line = line.split("#")[0]
            if self.get_number_drones(line):
                continue
            raise FormatError(f"[Line {i + 1}] Format error: Following line correspond to no parseable format.")          
    
    def get_number_drones(self, line: str) -> bool:
        if not self.start:
            return False

        if re.match(self.nb_drones_regex ,line):
            self.nb_drones
            return True
        raise ValueError("")
    
    def ignore_line(self, line: str) -> bool:
        line = line.strip()
        if line.startswith("#"):
            return True
        return False