from src.parsing.parser import Parser
from src.algo.Dijkstra import Dijkstra
from src.visual.map_visual import MapVisual
from src.visual import PyQt6 as PyQt


class MapsManager():
    """Handle map creation and visual"""
    def __init__(self, root: PyQt.QEntity) -> None:
        """Instantiate object for pipeline"""
        self.parser = Parser()
        self.algo = Dijkstra()
        self.visual = MapVisual(root)

    def create_maps(self, filename: str) -> bool:
        """Create a map with parsing, path finding and visual representation"""
        self.graph = self.parser.get_data_files(filename)
        if not self.graph:
            return False
        drones = self.algo.get_drones_path(self.graph)
        self.graph.hashmap = self.algo.drones_turn
        if not drones:
            print("No path found")
            return False
        self.graph.create_drones(drones)
        self.visual.create_maps(self.graph)
        self.print_turns()
        return True

    def print_turns(self) -> None:
        if not self.graph:
            return
        for i in range(self.graph.stats.nb_turns):
            for drone in self.graph.drones:
                if (len(drone.hub_turns) > i + 1 and drone.hub_turns[i] !=
                        drone.hub_turns[i + 1]):
                    print(f"{drone.name}-{drone.hub_turns[i + 1].name}",
                          end=" ")
            print()
