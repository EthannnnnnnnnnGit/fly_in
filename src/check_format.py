import re


class CheckFormat():
    def __init__(self):
        self.nb_drones_regex = r"^nb_drones:\s*(\d+)$"

    def is_drones_first_line(self, lines: list[str]):
        for line in lines:
            pass
    
    def get_number_drones(self, line: str) -> bool:
        if re.match(self.nb_drones_regex ,line):
            self.nb_drones
            return True
        return False