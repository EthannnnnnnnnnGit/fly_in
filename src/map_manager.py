from src.parsing.parser import Parser
from src.algo.Dijkstra import Dijkstra
from src.visual.map_visual import MapVisual
from src.visual import PyQt6 as PyQt


class MapsManager():
    def __init__(self, root: PyQt.QEntity) -> None:
        self.parser = Parser()
        self.algo = Dijkstra()
        self.visual = MapVisual(root)

    def create_maps(self, filename: str) -> bool:
        self.graph = self.parser.get_data_files(filename)
        if not self.graph:
            return False
        drones = self.algo.get_drones_path(self.graph)
        if not drones:
            print("No path found")
            return False
        self.graph.create_drones(drones)
        self.visual.create_maps(self.graph)
        return True
