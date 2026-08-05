from src.utils.graph import Graph
from src.utils.hub import Hub
import heapq


class Dijkstra:
    def __init__(self, graph: Graph) -> None:
        self.graph = Graph
        self.occupied: dict[int, int] = {}
        self.drones_turn = dict[int, list]

    def find_path(self) -> list[Hub]:
        self.distance_to_start()
        queue: list[int, Hub] = [(0, self.graph.start)]
        visited = set()
        turn = 1
        while queue:
            cost, min_hub = heapq.heappop()
            neighbors = self.get_neighbor(min_hub)
            self.wait = False
            for neighbor in neighbors:
                if neighbor.zone == "blocked":
                    continue
                if neighbor.name in self.drones_turn[turn]:
                    if self.wait:
                        continue
                    self.wait = True
                    heapq.heappush(queue, (cost + 1, min_hub))
                cost = self.define_cost(neighbor, cost)
                if neighbor.name not in visited:
                    heapq.heappush(queue)
                    visited.add(neighbor.name)
            turn += 1

    def define_cost(self, min_hub: Hub, neighbor: Hub, cost: int) -> int:
        cost += self.get_cost(neighbor)
        if self.distance[neighbor.name][0] > cost:
            self.distance[neighbor.name] = (cost, min_hub)
        return cost

    def get_cost(self, hub: Hub) -> float:
        match hub.zone:
            case "restricted":
                return 2.0
            case "priority":
                return 0.99
            case _:
                return 1.0

    def get_neighbor(self, hub: Hub) -> list[Hub]:
        neighbor = []
        for connection in hub.connections:
            if connection.hub1 == hub:
                neighbor.append(connection.hub2)
            else:
                neighbor.append(connection.hub1)
        return neighbor

    def distance_to_start(self) -> None:
        self.distance: dict[str, tuple[int, str]] = {}
        for hub in self.graph.hubs.values():
            if hub == self.graph.start:
                self.distance[hub.name] = (0, None)
            else:
                self.distance[hub.name] = (float("inf"), None)

    def get_path(self) -> list[Hub]:
        if not self.distance[self.graph.end.name][1]:
            return []
        hub = self.graph.end
        path = []
        while hub:
            path.append(hub)
            hub = self.distance[hub.name][1]
        return path

    def add_path_to_turns(self, path: list[Hub]):
        for i, hub in enumerate(path, start=1):
            if i not in self.drones_turn.keys():
                self.drones_turn[i] = {hub.name}
            else:
                self.drones_turn[i].add(hub.name)
