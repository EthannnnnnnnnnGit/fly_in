from src.utils.hub import Hub, ZoneType
import re
from typing import Any


class HubManager:
    def create_hubs(self, data: dict, nb_drones: int):
        hubs = {}
        self.nb_drones = nb_drones
        self.names = set()
        self.coordinates = set()
        self.start = False
        self.end = False
        try:
            for i, line in data:
                self.line = i
                valid_data = self.extract_data(line)
                hubs[valid_data["name"]] = Hub(**valid_data)
            if not self.start:
                print("Value error: start hub missing")
                return {}
            if not self.end:
                print("Value error: end hub missing")
                return {}
        except Exception as e:
            print(f"[Line {self.line}] {e}")
            return {}
        return hubs

    def extract_data(self, line: str) -> dict[str, Any]:
        seperate = line.split("[")
        data = self.check_data(seperate[0])
        if len(seperate) > 1:
            metadata = self.check_metadata(seperate[1].strip("]"),
                                           data["type"])
        else:
            metadata = self.check_metadata("", data["type"])
        data.update(metadata)
        return data

    def check_data(self, data: str) -> dict[str, str | tuple[int, int]]:
        type, name, x, y = data.split()
        x, y = int(x), int(y)
        if not re.match(r"^(start_hub|end_hub|hub):$", type):
            raise ValueError("Value error: Zone type should be either "
                             "start_hub, end_hub or hub")
        if type == "start_hub:":
            if self.start is True:
                raise ValueError("Value error: can't have twice start hub")
            self.start = True
        if type == "end_hub:":
            if self.end is True:
                raise ValueError("Value error: can't have twice end hub")
            self.end = True
        if "-" in name:
            raise ValueError("Value error: Zone's name should not "
                             "contains a dash.")
        if name in self.names:
            raise ValueError("Value error: Two hubs cannot have the same name")
        if (x, y) in self.coordinates:
            raise ValueError("Value error: Can't have the same "
                             "coordinates twice.")
        self.names.add(name)
        self.coordinates.add((x, y))
        return {
            "type": type.strip(":"),
            "name": name,
            "coordinates": (x, y)
        }

    def check_metadata(self, data: str, type: str) -> dict:
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
                raise ValueError(f"Value error: Metadata {key} is not known.")
            match key:
                case "zone":
                    if value not in ZoneType:
                        raise ValueError("Value error: Zone value should be "
                                         "either normal, blocked, "
                                         "restricted or priority.")
                case "color":
                    pass
                case "max_drones":
                    if type == "start_hub" or type == "end_hub":
                        continue
                    try:
                        if int(value) < 0:
                            raise Exception
                    except Exception:
                        raise ValueError("Value error: max_drones value "
                                         "should be a valid positive integer.")
            used.add(key)
            metadata[key] = value
        if type == "start_hub" or type == "end_hub":
            metadata["max_drones"] = self.nb_drones
        return metadata
