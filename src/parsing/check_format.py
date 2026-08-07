import re
from .error import FormatError
from typing import Any


class CheckFormat:
    def __init__(self):
        self.nb_drones_regex = r"^nb_drones:\s+([\d\.\+-]+)$"
        self.metadata_regex = r"(\s+\[\s*([\w\.\+-]+=[\w\.\+-]+){1}"\
            r"(\s+[\w\.\+-]+[=][\w\.\+-]+)*\s*\])?$"
        self.hub_regex = r"^(start_hub|end_hub|hub):\s+([^\s]+)"\
            r"\s+(-?[\d]+)\s+(-?[\d]+)"
        self.connection_regex = r"^connection:\s+([^\s-]+-[^\s-]+)"

    def reset_parsing(self) -> None:
        self.start = True
        self.hubs: list[str] = []
        self.connections: list[str] = []

    def check_format(self, lines: list[str]) -> dict[str, Any]:
        self.reset_parsing()
        for i, line in enumerate(lines, 1):
            self.line = i
            try:
                if self.ignore_line(line):
                    continue
                line = line.split("#")[0].strip()
                if self.get_number_drones(line):
                    continue
                if self.get_hub(line):
                    continue
                if self.get_connection(line):
                    continue
                raise FormatError("Format error: Following line correspond "
                                  "to no parseable format.")
            except Exception as e:
                print(f"[Line {i}] {e}")
                return None
        return {
            "nb_drones": self.nb_drones,
            "hubs": self.hubs,
            "connections": self.connections
        }

    def ignore_line(self, line: str) -> bool:
        line = line.strip()
        if line.startswith("#"):
            return True
        if not line:
            return True
        return False

    def get_number_drones(self, line: str) -> bool:
        if not self.start:
            return False

        if re.match(self.nb_drones_regex, line):
            self.start = False
            self.nb_drones = int(line.split(":")[1])
            if self.nb_drones < 1:
                raise ValueError("Value error: Should have at least one drone")
            if self.nb_drones > 100:
                raise ValueError("Value error: Number of drones "
                                 "can't exceed 100.")
            return True
        raise ValueError("Value error: first parseable line should be "
                         "the number of drones format")

    def get_hub(self, line: str) -> bool:
        if not re.match(r"^(start_hub|end_hub|hub)", line):
            return False
        if re.match(self.hub_regex + self.metadata_regex, line):
            self.hubs.append((self.line, line))
            return True
        raise ValueError("Value error: String does not match hub format")

    def get_connection(self, line: str) -> bool:
        if not re.match(r"^connection", line):
            return False
        if re.match(self.connection_regex + self.metadata_regex, line):
            self.connections.append((self.line, line))
            return True
        raise ValueError("Value error: String does not "
                         "match connection format")
