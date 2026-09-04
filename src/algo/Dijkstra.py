from src.utils.graph import Graph
from src.utils.hub import Hub, ZoneType
from src.utils.connection import Connection
import heapq
from math import ceil


class Dijkstra:
    def reset_attributes(self, graph: Graph):
        self.graph = graph
        self.drones_turn: dict[int, dict[str, int]] = {}

    def get_drones_path(self, graph: Graph):
        self.reset_attributes(graph)
        paths: dict[str, list[Hub]] = {}
        for i in range(1, graph.nb_drones + 1):
            self.find_path()
            path = self.get_path()
            if not path:
                return {}
            self.add_path_to_turns(path)
            paths[f"D{i}"] = path
        return paths

    def find_path(self) -> None:
        self.distance_to_start()
        queue: list[tuple[int | float, Hub]] = [(0, 0, self.graph.start)]
        visited = {self.graph.start.name}
        i = 1
        while queue:
            cost, _,  min_hub = heapq.heappop(queue)
            neighbors = self.get_neighbor(min_hub)
            self.wait = False
            for neighbor, connection in neighbors:
                if neighbor.zone == "blocked" or neighbor.name in visited:
                    continue
                if self.should_wait(neighbor, connection, cost):
                    if self.wait:
                        continue
                    self.wait = True
                    heapq.heappush(queue, (cost + 1, i, min_hub))
                    i += 1
                    continue
                neighbor_cost = self.update_cost(min_hub, neighbor, cost)
                heapq.heappush(queue, (neighbor_cost, i, neighbor))
                i += 1
            visited.add(min_hub.name)

    def should_wait(self, neighbor: Hub, connection: Connection,
                    turn: float | int) -> bool:
        turn = ceil(turn) + 1
        if neighbor.zone == ZoneType.RESTRICTED:
            if (self.drones_turn.get(turn + 1)
                and self.drones_turn[turn + 1].get(connection.name) and
                    self.drones_turn[turn + 1][connection.name] >=
                    connection.capacity):
                return True
            turn += 1
        if (self.drones_turn.get(turn + 1) and
            self.drones_turn[turn + 1].get(connection.name) and
                self.drones_turn[turn + 1][connection.name] >=
                connection.capacity):
            return True
        if (self.drones_turn.get(turn + 1) and
            self.drones_turn[turn + 1].get(neighbor.name) and
                self.drones_turn[turn + 1][neighbor.name] >=
                neighbor.max_drones):
            return True
        return False

    def update_cost(self, hub: Hub, neighbor: Hub, cost: int) -> float:
        cost += self.get_cost(neighbor)
        if self.distance[neighbor.name][0] > cost:
            self.distance[neighbor.name] = (cost, hub)
        return cost

    def get_cost(self, hub: Hub) -> float:
        match hub.zone:
            case ZoneType.RESTRICTED:
                return 2.0
            case ZoneType.PRIORITY:
                return 0.999
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
        self.distance: dict[str, tuple[int, Hub]] = {}
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
        prev = ceil(self.distance[hub.name][0]) + 1
        while hub:
            for i in range(prev - ceil(self.distance[hub.name][0])):
                path.append(hub)
            prev = prev = ceil(self.distance[hub.name][0])
            hub = self.distance[hub.name][1]
        return path[::-1]

    def add_path_to_turns(self, paths: list[Hub]):
        turn = 1
        for i in range(len(paths) - 1):
            hub = paths[i]
            connection = [connection for connection in hub.connections
                          if connection in paths[i + 1].connections][0]
            if hub.zone == ZoneType.RESTRICTED:
                self.add_hub(connection, turn)
                turn += 1
            self.add_hub(connection, turn)
            self.add_hub(hub, turn)
            turn += 1

    def add_hub(self, hub, turn):
        if not self.drones_turn.get(turn):
            self.drones_turn[turn] = {hub.name: 1}
        elif not self.drones_turn[turn].get(hub.name):
            self.drones_turn[turn][hub.name] = 1
        else:
            self.drones_turn[turn][hub.name] += 1
