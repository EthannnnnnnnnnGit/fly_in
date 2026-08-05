from src.utils.hub import Hub
from src.utils.connection import Connection
from typing import Any


class ConnectionManager:
    def add_connections(self, hubs: dict[str, Hub],
                        connections: tuple[int, str]) -> bool:
        self.pairs_done = set()
        for line, connection in connections:
            self.line = line
            try:
                data = self.get_connection_data(hubs, connection)
                if not data:
                    return None
            except Exception as e:
                print(f"[Line {line}] {e}")
                return None
            else:
                hubs = self.create_connection(data, hubs)
        return hubs

    def get_connection_data(self, hubs: dict[str, Hub],
                            connection: str) -> dict[str, Any]:
        seperate = connection.split("[")
        try:
            data = seperate[0]
            if len(seperate) > 1:
                metadata = self.check_metadata(seperate[1].strip("]"))
            else:
                metadata = self.check_metadata("")
            connection = self.check_connection(hubs, data)
            connection.update(metadata)
            return connection
        except Exception as e:
            print(f"[Line {self.line}] {e}")
            return {}

    def check_connection(self, hubs: dict[str, Hub], connection: str) -> None:
        connection = connection.split()[1]
        first, second = connection.split("-")
        if first == second:
            raise ValueError("Value error: can't have a connection "
                             "with the same name twice")
        if first not in hubs.keys():
            raise ValueError(f"Value error: hub {first} is not defined.")
        if second not in hubs.keys():
            raise ValueError(f"Value error: hub {second} is not defined.")
        if ((first, second) in self.pairs_done or
                (second, first) in self.pairs_done):
            raise ValueError("Value error: Connection has already "
                             "been defined")
        self.pairs_done.add((first, second))
        return {"name": connection, "hub1": first, "hub2": second}

    def check_metadata(self, data: str):
        metadata = {"capacity": 1}
        if not data:
            return metadata
        if len(data.split()) > 1:
            raise ValueError("Value error: Should have only one metadata, "
                             "for connections: max_link_capacity")
        key, value = data.split("=")
        if key != "max_link_capacity":
            raise ValueError("Value error: Unknown metadata key, "
                             "max_link_capacity is the only one available")
        try:
            if int(value) < 0:
                raise Exception
        except Exception:
            raise ValueError("Value error: max link capacity should be a "
                             "valid positive integer or zero")
        return metadata

    def create_connection(self, data: dict[str, str | int],
                          hubs: dict[str, Hub]) -> dict[str, Hub]:
        data["hub1"] = hubs[data["hub1"]]
        data["hub2"] = hubs[data["hub2"]]
        connection = Connection(**data)
        connection.hub1.connections.append(connection)
        connection.hub2.connections.append(connection)
        return hubs
