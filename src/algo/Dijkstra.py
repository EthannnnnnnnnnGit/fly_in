from src.utils.graph import Graph
from src.utils.hub import Hub, ZoneType
from src.utils.connection import Connection
import heapq
from math import ceil


class Dijkstra:
    """
    Path solving class using Dijkstra algorithm
    """
    def reset_attributes(self, graph: Graph) -> None:
        """Set all attribut to default for new maps pathfinding"""
        self.graph = graph
        self.drones_turn: dict[int, dict[str, int]] = {}

    def get_drones_path(self, graph: Graph) -> dict[str, list[Hub |
                                                              Connection]]:
        """Run dijkstra nb of drones times"""
        self.reset_attributes(graph)
        paths: dict[str, list[Hub | Connection]] = {}
        for i in range(1, graph.nb_drones + 1):
            self.find_path()
            path = self.get_path()
            if not path:
                return {}
            self.add_path_to_turns(path)
            paths[f"D{i}"] = path
        return paths

    def find_path(self) -> None:
        """Run Dijkstra algorithm"""
        self.distance_to_start()
        queue: list[tuple[int | float, int, Hub]] = [(0, 0, self.graph.start)]
        visited: set[str] = {self.graph.start.name}
        i = 1
        while queue:
            cost, _,  min_hub = heapq.heappop(queue)
            neighbors = self.get_neighbor(min_hub)
            self.wait = False
            for neighbor, connection in neighbors:
                if (neighbor.zone == ZoneType.BLOCKED or
                        neighbor.name in visited):
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
        """
        Define if a drone should wait depending of the
        availablity of the neighbor hub and connections

        Keyword arguments:
        neighbor -- neighbor's hub
        connection -- neighbor's connection
        turn -- define the turn disponibility to check
        """
        turn = ceil(turn)
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

    def update_cost(self, hub: Hub, neighbor: Hub, cost: int | float) -> float:
        """Update the cost of the neighbor"""
        cost += self.get_cost(neighbor)
        if self.distance[neighbor.name][0] > cost:
            self.distance[neighbor.name] = (cost, hub)
        return cost

    def get_cost(self, hub: Hub) -> float:
        """Define the cost depending of hub type"""
        match hub.zone:
            case ZoneType.RESTRICTED:
                return 2.0
            case ZoneType.PRIORITY:
                return 0.999
            case _:
                return 1.0

    def get_neighbor(self, hub: Hub) -> list[tuple[Hub, Connection]]:
        """Return the list of neighbor of a hub with their connections"""
        neighbor = []
        for connection in hub.connections:
            if connection.hub1 == hub:
                neighbor.append((connection.hub2, connection))
            else:
                neighbor.append((connection.hub1, connection))
        return neighbor

    def distance_to_start(self) -> None:
        """Define default distance from start (infinity)"""
        self.distance: dict[str, tuple[int | float, Hub | None]] = {}
        for hub in self.graph.hubs.values():
            if hub == self.graph.start:
                self.distance[hub.name] = (0, None)
            else:
                self.distance[hub.name] = (float("inf"), None)

    def get_path(self) -> list[Hub | Connection]:
        """Get the path find by the algorithm"""
        if not self.distance[self.graph.end.name][1]:
            return []
        hub = self.graph.end
        path: list[Connection | Hub] = []
        prev = ceil(self.distance[hub.name][0]) + 1
        while hub:
            for _ in range(prev - ceil(self.distance[hub.name][0])):
                path.append(hub)
            prev = ceil(self.distance[hub.name][0])
            next = self.distance[hub.name][1]
            if next is None:
                break
            if hub.zone == ZoneType.RESTRICTED:
                prev -= 1
                path.append([connection for connection in hub.connections
                            if next and connection in
                            next.connections][0])
            hub = next
        return path[::-1]

    def add_path_to_turns(self, paths: list[Hub | Connection]) -> None:
        """Add the found path to the hashmap"""
        self.add_hub(paths[0], 0)
        for i in range(1, len(paths)):
            hub = paths[i]
            if isinstance(hub, Connection):
                self.add_hub(hub, i)
                continue
            if isinstance(paths[i - 1], Connection):
                connection = paths[i - 1]
            else:
                neighbor = paths[i - 1]
                if not isinstance(neighbor, Connection):
                    connection = [connection for connection in hub.connections
                                  if connection in neighbor.connections][0]
            if hub != paths[i - 1]:
                self.add_hub(connection, i)
            self.add_hub(hub, i)

    def add_hub(self, hub: Hub | Connection, turn: int) -> None:
        """Add the hub or connection in the hashmap"""
        if not self.drones_turn.get(turn):
            self.drones_turn[turn] = {hub.name: 1}
        elif not self.drones_turn[turn].get(hub.name):
            self.drones_turn[turn][hub.name] = 1
        else:
            self.drones_turn[turn][hub.name] += 1
