import re
from .error import FormatError


class CheckFormat():
    def __init__(self):
        self.nb_drones_regex = r"^nb_drones:\s*(\d+)$"

    def is_drones_first_line(self, lines: list[str]):
        self.start = True
        for i, line in enumerate(lines):
            try:
                if self.ignore_line(line):
                    continue
                line = line.split("#")[0]
                if self.get_number_drones(line):
                    continue
                raise FormatError("Format error: Following line correspond "
                                  "to no parseable format.")
            except Exception as e:
                print(f"[Line {i + 1}] {e}")

    def get_number_drones(self, line: str) -> bool:
        if not self.start:
            return False

        if re.match(self.nb_drones_regex, line):
            self.start = False
            self.nb_drones = int(line.split(":")[1])
            return True
        raise ValueError("Value error: first parseable line should be "
                         "the number of drones")

    def ignore_line(self, line: str) -> bool:
        line = line.strip()
        if line.startswith("#"):
            return True
        return False
