from src.utils.hub import Hub
from typing import Any


class ConnectionManager:
    def add_connections(self, hubs: dict[str, Hub],
                            connections: tuple[int, str]) -> bool:
            self.pairs_done = set()
            for line, connection in connections:
                try:
                    data = self.get_connections_data(hubs, connection)
                except Exception as e:
                    print(f"[{line}] {e}")
                    return None
            return hubs

    def get_connections_data(self, hubs: dict[str, Hub], 
                             connection: str) -> dict[str, Any]:
        seperate = connection.split("[")
        try:
            data = seperate[0]
            if len(seperate) > 1:
                metadata = self.check_metadata(seperate[1].strip("]"))
            else:
                metadata = self.check_metadata("")
            self.check_connections()
            data.update(metadata)
            return data
        except Exception as e:
            print(f"[Line {self.line}] {e}")
            return {}

    def check_connections(self, hubs: dict[str, Hub], connection: str) -> None:
        pass

    def check_metadata(self, metadata: str):
        metadata = {"max_link_capacity": 1}
        if not metadata:
            return metadata
        if len(metadata.split()) > 1:
            raise ValueError("Value error: Should have only one metadata, "
                             "for connections: max_link_capacity")
        key, value = metadata.split("=")
        if key != "max_link_capacity":
            raise ValueError("Value error: Unknown metadata key, "
                             "max_link_capacity is the only one available")
        try:
            if int(value) < 0:
                raise Exception
        except Exception:
            raise ValueError("Value error: max link capacity should be a "
                             "valid positive integer or zero")
