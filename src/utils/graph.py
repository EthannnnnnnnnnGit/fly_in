from .hub import Hub


class Graph:
    start: Hub
    end: Hub

    def __init__(self, hubs: list[Hub], nb_drones: int):
        self.hubs: dict[str, Hub] = {val.name: val for val in hubs}
        self.nb_drones = nb_drones
        self.get_connections()

    def define_start_end(self) -> None:
        for hub in self.hubs:
            if hub.type == "start_hub":
                self.start = hub
            if hub.type == "end_hub":
                self.end = hub

    def get_connections(self):
        self.connections = []
        for hub in self.hubs.values():
            for connection in hub.connections:
                if connection not in self.connections:
                    self.connections.append(connection)
