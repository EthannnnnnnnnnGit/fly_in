from src.utils.graph import Graph
from src.utils.hub import Hub
from src.utils.connection import Connection
import heapq

# {1: {"hub1": 5, "connection": 1}}
# {1: ["hub1", "hub1"].count("hub1")}


class Dijkstra:
    def reset_attributes(self, graph: Graph):
        self.graph = graph
        self.occupied: dict[int, int] = {}
        self.drones_turn = dict[int, list]

    def find_path(self, graph: Graph) -> list[Hub | Connection]:
        self.reset_attributes(graph)
        self.distance_to_start()
        queue: dict[int, list[int, Hub]] = {1: [(0, self.graph.start)]}
        visited = {self.graph.start.name}
        turn = 1
        while queue[turn]:
            cost, min_hub = heapq.heappop()
            neighbors = self.get_neighbor(min_hub)
            self.wait = False
            for neighbor, connection in neighbors:
                if neighbor.zone == "blocked":
                    continue
                if self.should_wait(neighbor, connection):
                    if self.wait:
                        continue
                    self.wait = True
                    heapq.heappush(queue[turn], (cost + 1, min_hub))
                    continue
                cost = self.define_cost(neighbor, cost)
                if neighbor.name not in visited:
                    heapq.heappush(queue, (cost, neighbor))
                    visited.add(neighbor.name)
            turn += 1 if not turn else turn
            turn += 1 if not turn else turn

    def should_wait(self, neighbor: Hub) -> bool:
        if neighbor.zone == "restricted":
            pass

    def push_to_queue(self, neighbor: Hub, queue: list, turn: int) -> list:
        ...

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

    def get_neighbor(self, hub: Hub) -> list[Hub, Connection]:
        neighbor = []
        for connection in hub.connections:
            if connection.hub1 == hub:
                neighbor.append((connection.hub2, connection))
            else:
                neighbor.append((connection.hub1, connection))
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
