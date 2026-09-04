from src.parsing.parser import Parser
from src.algo.Dijkstra import Dijkstra
from src.visual.map_visual import MapVisual


class MapsManager():
    def __init__(self, root):
        self.parser = Parser()
        self.algo = Dijkstra()
        self.visual = MapVisual(root)

    def create_maps(self, filename: str):
        graph = self.parser.get_data_files(filename)
        if not graph:
            return
        drones = self.algo.get_drones_path(graph)
        if not drones:
            print("No path found")
            return
        self.visual.create_maps(graph)
