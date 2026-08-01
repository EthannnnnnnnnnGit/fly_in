from src.utils.hub import Hub, ZoneType
import re
from typing import Any


class HubManager:
    def create_hubs(self, data: list[tuple[int, str]]):
        hubs = {}
        self.names = set()
        for i, line in data:
            self.line = i
            valid_data = self.extract_data(line)
            if not valid_data:
                return {}
            hubs[valid_data["name"]] = Hub(**valid_data)
        return hubs

    def extract_data(self, line: str) -> dict[str, Any]:
        seperate = line.split("[")
        try:
            data = self.check_data(seperate[0])
            if len(seperate) > 1:
                metadata = self.check_metadata(seperate[1].strip("]"))
            else:
                metadata = self.check_metadata("")
            data.update(metadata)
            return data
        except Exception as e:
            print(f"[Line {self.line}] {e}")
            return {}

    def check_data(self, data: str) -> dict[str, str | tuple[int, int]]:
        type, name, x, y = data.split()
        if not re.match(r"^(start_hub|end_hub|hub):$", type):
            raise ValueError("Value error: Zone type should be either "
                             "start_hub, end_hub or hub")
        if "-" in name:
            raise ValueError("Value error: Zone's name should not "
                             "contains a dash.")
        if name in self.names:
            raise ValueError("Value error: Two hubs cannot have the same name")
        x, y = int(x), int(y)
        return {
            "type": type.strip(":"),
            "name": name,
            "coordinates": (x, y)
        }

    def check_metadata(self, data: str) -> dict:
        metadata = {"zone": "normal", "color": None, "max_drones": 1}
        if not data:
            return metadata
        used = set()
        for meta in data.split():
            key, value = meta.split("=")
            if key in used:
                raise ValueError(f"Value error: Metadata {key} should not "
                                 "appear twice.")
            if key not in metadata.keys():
                raise ValueError("Value error: Metadata {key} is not known.")
            match key:
                case "zone":
                    if value not in ZoneType:
                        raise ValueError("Value error: Zone value should be "
                                         "either normal, blocked, "
                                         "restricted or priority.")
                case "color":
                    pass
                case "max_drones":
                    try:
                        if int(value) < 0:
                            raise Exception
                    except Exception:
                        raise ValueError("Value error: max_drones value "
                                         "should be a valid positive integer.")
            used.add(key)
            metadata[key] = value
        return metadata
