from src.parsing.check_format import CheckFormat
from src.parsing.create_hubs import HubManager
from src.parsing.connections_manager import ConnectionManager
from src.utils.graph import Graph


class Parser:
    """
    Handle parsing from given file, from reading to value checks
    """
    def __init__(self) -> None:
        """Instantiate pipeline"""
        self.format = CheckFormat()
        self.hub = HubManager()
        self.connections = ConnectionManager()

    def read_file(self, filename: str) -> None:
        """Read the file by lines"""
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
        except OSError:
            print("An error as occured while attempting to reach files data")
            self.lines = None
        else:
            self.lines = lines

    def get_data_files(self, filename: str) -> Graph | None:
        """Check files data with pipeline"""
        self.read_file(filename)
        if not self.lines:
            return None
        data = self.format.check_format(self.lines)
        if not data:
            return None
        hubs = self.hub.create_hubs(data["hubs"], data["nb_drones"])
        if not hubs:
            return None
        hubs = self.connections.add_connections(hubs,
                                                self.hub.hub_line,
                                                data["connections"])
        if not hubs:
            return None
        graph = Graph(hubs.values(), data["nb_drones"])
        return graph
