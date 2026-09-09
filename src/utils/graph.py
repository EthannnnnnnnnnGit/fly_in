from src.utils.hub import Hub
from src.utils.drones import Drones
from src.utils.stats import Stats
from src.utils.connection import Connection


class Graph:
    start: Hub
    end: Hub

    def __init__(self, hubs: list[Hub], nb_drones: int) -> None:
        self.hubs: dict[str, Hub] = {val.name: val for val in hubs}
        self.nb_drones = nb_drones
        self.get_connections()
        self.define_start_end()
        self.stats = Stats(self)

    def define_start_end(self) -> None:
        for hub in self.hubs.values():
            if hub.type.value == "start_hub":
                self.start = hub
            if hub.type.value == "end_hub":
                self.end = hub

    def get_connections(self) -> None:
        self.connections: list[Connection] = []
        for hub in self.hubs.values():
            for connection in hub.connections:
                if connection not in self.connections:
                    self.connections.append(connection)

    def create_drones(self, drones_turn: dict[str, list[Hub]]) -> None:
        self.drones = []
        for name, hubs in drones_turn.items():
            self.drones.append(Drones(name, hubs, None))
