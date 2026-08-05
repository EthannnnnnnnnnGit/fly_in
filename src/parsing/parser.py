from .check_format import CheckFormat
from .create_hubs import HubManager
from .connections_manager import ConnectionManager
from src.utils.graph import Graph


class Parser:
    def __init__(self):
        self.format = CheckFormat()
        self.hub = HubManager()
        self.connections = ConnectionManager()

    def read_file(self, filename: str) -> None:
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
        except OSError:
            print("An error as occured while attempting to reach files data")
            self.lines = None
        else:
            self.lines = lines

    def get_data_files(self, filename: str):
        self.read_file(filename)
        if not self.lines:
            return
        data = self.format.check_format(self.lines)
        if not data:
            return
        hubs = self.hub.create_hubs(data["hubs"], data["nb_drones"])
        if not hubs:
            return
        hubs = self.connections.add_connections(hubs, data["connections"])
        if not hubs:
            return
        print("\n=============\n")
        for hub in hubs.values():
            hub.get_attributes()
            print("\n=============\n")
        graph = Graph(hubs.values(), data["nb_drones"])
        return graph
