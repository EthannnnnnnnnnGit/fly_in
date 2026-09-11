from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.utils.graph import Graph


class Stats():
    """
    Class that contains graph data for visual
    """
    def __init__(self, graph: Graph):
        self.define_limits(graph)
        self.get_middle()

    def define_limits(self, graph: Graph) -> None:
        """Define the max coordinates of the graph"""
        self.min_x, self.max_x, self.min_z, self.max_z = 0, 0, 0, 0
        for hub in graph.hubs.values():
            x, z = hub.coordinates
            z = -z
            self.min_x = x if x < self.min_x else self.min_x
            self.max_x = x if x > self.max_x else self.max_x
            self.min_z = z if z < self.min_z else self.min_z
            self.max_z = z if z > self.max_z else self.max_z

    def get_middle(self) -> None:
        """Find the middle coordinates of the graph"""
        self.middle_x = (self.min_x * 15 + self.max_x * 15) / 2
        self.scale_x = (abs(self.min_x * 15) + abs(self.max_x * 15)) + 20
        self.middle_z = (self.min_z * 15 + self.max_z * 15) / 2
        self.scale_z = (abs(self.min_z * 15) + abs(self.max_z * 15)) + 20

    def get_nb_turns(self, graph: Graph) -> None:
        """Get the max number of drones for the graph"""
        self.nb_turns = 0
        for drone in graph.drones:
            if len(drone.hub_turns) - 1 > self.nb_turns:
                self.nb_turns = len(drone.hub_turns) - 1
