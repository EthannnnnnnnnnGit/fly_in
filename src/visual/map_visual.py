import src.visual.PyQt6 as PyQt
from src.utils.graph import Graph
from src.utils.connection import Connection
from src.utils.hub import Hub
from src.utils.drones import Drones
from PyQt6.sip import isdeleted
import math
from typing import cast


class MapVisual():
    """
    Class that handle visual of the graph and map
    """
    anim_timer: PyQt.QTimer

    def __init__(self, root: PyQt.QEntity) -> None:
        """Instantiate important attributes"""
        self.root = root
        self.color = {"normal": "#6495ED", "blocked": "#D70040",
                      "restricted": "#FFA500", "priority": "#00FFFF"}
        self.is_processing = False
        self.run = False
        self.define_turn()

    def define_turn(self):
        first = [(x / 100, z / 100) for x in range(10, 0, -1)
                 for z in range(0, 10, 1)]
        second = [(x / 100, z / 100) for x in range(0, -10, -1)
                  for z in range(10, 0, -1)]
        third = [(x / 100, z / 100) for x in range(-10, 0, 1)
                 for z in range(0, -10, -1)]
        fourth = [(x / 100, z / 100) for x in range(0, 10, 1)
                  for z in range(-10, 0, 1)]
        self.rotate = first + second + third + fourth

    def create_maps(self, graph: Graph) -> None:
        """Create floor, hubs, connection and drones"""
        self.graph = graph
        for hub in graph.hubs.values():
            x, z = hub.coordinates
            z = -z
            self.create_hub((x * 15, z * 15), hub.color, hub.zone.value)
        for connection in graph.connections:
            x1, z1 = connection.hub1.coordinates
            x2, z2 = connection.hub2.coordinates
            self.create_river((x1 * 15, z1 * 15), (x2 * 15, z2 * 15))
        self.make_grass()
        self.create_drones()

    def make_grass(self) -> None:
        """Create the floor for the visual"""
        grass = PyQt.QEntity(self.root)

        mesh = PyQt.QCuboidMesh()

        transform = PyQt.QTransform()
        transform.setTranslation(PyQt.QVector3D(self.graph.stats.middle_x, 0,
                                                self.graph.stats.middle_z))
        transform.setScale3D(PyQt.QVector3D(self.graph.stats.scale_x - 5, 1,
                                            self.graph.stats.scale_z - 5))

        material = PyQt.QPhongMaterial()
        material.setDiffuse(PyQt.QColor("#267001"))

        grass.addComponent(mesh)
        grass.addComponent(transform)
        grass.addComponent(material)

        dirt = PyQt.QEntity(self.root)

        mesh = PyQt.QCuboidMesh()

        transform = PyQt.QTransform()
        transform.setTranslation(PyQt.QVector3D(self.graph.stats.middle_x,
                                                -0.6,
                                                self.graph.stats.middle_z))
        transform.setScale3D(PyQt.QVector3D(self.graph.stats.scale_x, 1,
                                            self.graph.stats.scale_z))

        material = PyQt.QPhongMaterial()
        material.setDiffuse(PyQt.QColor("#63452C"))

        dirt.addComponent(mesh)
        dirt.addComponent(transform)
        dirt.addComponent(material)

    def create_hub(self, coordinates: tuple[float, float],
                   color: str | None, zone: str) -> None:
        """Create hub with given type, coordinate and color"""
        color = "blue" if not color else color
        x, z = coordinates
        y = 1
        scale = (4, 0.01, 4)

        hub = PyQt.QEntity(self.root)

        mesh = PyQt.QMesh()
        mesh.setSource(PyQt.QUrl.fromLocalFile("assets/lake.obj"))

        transform = PyQt.QTransform()
        transform.setTranslation(PyQt.QVector3D(x, y, z))
        transform.setScale3D(PyQt.QVector3D(*scale))

        material = PyQt.QPhongMaterial()
        material.setDiffuse(PyQt.QColor(self.color[zone]))

        hub.addComponent(mesh)
        hub.addComponent(transform)
        hub.addComponent(material)

        self.create_buoy((x, y, z), color)

    def create_buoy(self, coordinates: tuple[float, int, float],
                    color: str) -> None:
        """Create buoy at the middle of the hub"""
        color = "black" if not color else color
        hub = PyQt.QEntity(self.root)

        mesh = PyQt.QMesh()
        mesh.setSource(PyQt.QUrl.fromLocalFile("assets/buoy.obj"))

        transform = PyQt.QTransform()
        transform.setTranslation(PyQt.QVector3D(*coordinates))
        transform.setScale3D(PyQt.QVector3D(0.7, 0.7, 0.7))

        material = PyQt.QPhongMaterial()
        material.setDiffuse(PyQt.QColor(color))

        hub.addComponent(mesh)
        hub.addComponent(transform)
        hub.addComponent(material)

    def create_river(self, start: tuple[int, int],
                     end: tuple[int, int]) -> None:
        """Create connection as rivers"""
        x1, z1 = start[0], -start[1]
        x2, z2 = end[0], -end[1]

        middle = ((x1 + x2) / 2, 0.05, (z1 + z2) / 2)
        angle = math.degrees(math.atan2(z2 - z1, x2 - x1))
        lenght = math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2)

        river = PyQt.QEntity(self.root)

        mesh = PyQt.QMesh()
        mesh.setSource(PyQt.QUrl.fromLocalFile("assets/water.obj"))

        transform = PyQt.QTransform()
        transform.setTranslation(PyQt.QVector3D(*middle))
        transform.setScale3D(PyQt.QVector3D(lenght, 1, 2))
        transform.setRotation(PyQt.QQuaternion.fromAxisAndAngle(
            PyQt.QVector3D(0, 1, 0), -angle
        ))

        material = PyQt.QPhongMaterial()
        material.setDiffuse(PyQt.QColor("#6495ED"))

        river.addComponent(mesh)
        river.addComponent(transform)
        river.addComponent(material)

    def create_drones(self) -> None:
        """Instantiate every drone at the start hub"""
        self.turn = 0
        i = 1
        x, z = self.graph.start.coordinates
        for i, drone in enumerate(self.graph.drones):
            drone.entity = PyQt.QEntity(self.root)

            mesh = PyQt.QMesh()
            mesh.setSource(PyQt.QUrl.fromLocalFile("assets/boat.obj"))

            transform = PyQt.QTransform()
            transform.setTranslation(PyQt.QVector3D(x - 2, 1.35, z))
            transform.setScale3D(PyQt.QVector3D(0.33, 0.3, 0.3))
            transform.setRotation(PyQt.QQuaternion.fromAxisAndAngle(
                PyQt.QVector3D(0, 1, 0), 90
            ))

            material = PyQt.QPhongMaterial()
            material.setDiffuse(PyQt.QColor("#9D6C3C"))

            drone.entity.addComponent(mesh)
            drone.entity.addComponent(transform)
            drone.entity.addComponent(material)

    def run_simulation(self) -> None:
        if not hasattr(self, "sim_timer") or isdeleted(self.anim_timer):
            self.sim_timer = PyQt.QTimer(self.root)
            self.sim_timer.timeout.connect(self._step_simulation)

        self.sim_timer.start(100)

    def _step_simulation(self) -> None:
        if self.turn == self.graph.stats.nb_turns or not self.run:
            if self.turn == self.graph.stats.nb_turns and self.run:
                self.run = not self.run
            self.sim_timer.stop()
            return

        if not self.is_processing:
            self.change_turn(1)

    def change_turn(self, next_turn: int) -> None:
        """Visually process turn by moving drones"""
        if self.is_processing:
            return
        self.is_processing = True
        self.drones_updates = []
        for drone in self.graph.drones:
            mult: int | float = 15
            advancement: int | float = 1
            if (len(drone.hub_turns) <= self.turn + next_turn or
                len(drone.hub_turns) <= self.turn or
                    self.turn + next_turn < 0 or
                    (self.turn <= 0 and self.turn + next_turn <= 0)):
                continue
            if (drone.hub_turns[self.turn + next_turn] ==
                    drone.hub_turns[self.turn]):
                continue
            if (isinstance(drone.hub_turns[self.turn], Connection)):
                advancement = 0.5
                prev = cast(Hub, drone.hub_turns[self.turn - next_turn])
                next = cast(Hub, drone.hub_turns[self.turn + next_turn])
                x1, z1 = prev.coordinates
                x2, z2 = next.coordinates
            elif (isinstance(drone.hub_turns[self.turn + next_turn],
                             Connection)):
                mult = 7.5
                advancement = 0.5
                prev = cast(Hub, drone.hub_turns[self.turn])
                next = cast(Hub, drone.hub_turns[self.turn + 2 * next_turn])
                x1, z1 = prev.coordinates
                x2, z2 = next.coordinates
            else:
                prev = cast(Hub, drone.hub_turns[self.turn])
                next = cast(Hub, drone.hub_turns[self.turn + next_turn])
                x1, z1 = prev.coordinates
                x2, z2 = next.coordinates
            vector = PyQt.QVector3D((x2 - x1) * advancement, 0,
                                    (-(z2 - z1)) * advancement)
            goal_vector = PyQt.QVector3D(x1 * 15 + (x2 - x1) * mult, 1.35,
                                         -(z1 * 15 + (z2 - z1) * mult))
            self.drones_updates.append((drone, vector, goal_vector))
        if self.graph.stats.nb_turns >= self.turn + next_turn >= 0:
            self.turn += next_turn

        if hasattr(self, "anim_timer") and not isdeleted(self.anim_timer):
            if self.anim_timer.isActive():
                self.anim_timer.stop()

        self.anim_timer = PyQt.QTimer(self.root)
        self.anim_timer.setInterval(16)
        self.anim_timer.timeout.connect(self.set_frame)
        self.anim_timer.start()

    def set_frame(self) -> None:
        """Move drones with multiples frames"""
        stop = False
        if not self.drones_updates:
            self.anim_timer.stop()
            self.is_processing = False
        for drone, new_pos, goal in self.drones_updates:
            entity = drone.entity
            if entity:
                transform = entity.findChild(PyQt.QTransform)
            current_pos = transform.translation()
            transform.setTranslation(current_pos + new_pos)
            if current_pos + new_pos == goal:
                stop = True
                transform.setTranslation(goal)
        if stop:
            self.anim_timer.stop()
            self.is_processing = False

    def is_near_orbit_exit(
            self,
            boat_pos: PyQt.QVector3D,
            exit_pos: PyQt.QVector3D,
            hub_center: PyQt.QVector3D,
            angle_threshold_degrees: float = 5.0,
    ) -> bool:
        """
        Checks if the boat's current angle around the hub is within a
        specified threshold of the target exit angle.
        """
        # 1. Vectors relative to hub center
        current_vec = boat_pos - hub_center
        exit_vec = exit_pos - hub_center

        # 2. Get angles in radians on XZ plane
        angle_current = math.atan2(current_vec.z(), current_vec.x())
        angle_exit = math.atan2(exit_vec.z(), exit_vec.x())

        # 3. Calculate shortest angular difference (handles 0/360 boundary)
        diff_rad = math.atan2(
            math.sin(angle_current - angle_exit),
            math.cos(angle_current - angle_exit),
        )
        diff_deg = math.degrees(abs(diff_rad))

        # 4. Return True if within the angular tolerance zone
        return diff_deg <= angle_threshold_degrees

    def rotate_hub(self, drone: Drones, vector: PyQt.QVector3D) -> None:
        if hasattr(self, "anim_timer") and not isdeleted(self.anim_timer):
            if self.anim_timer.isActive():
                self.anim_timer.stop()
        goal = PyQt.QVector3D(vector)
        for i in range(len(self.turn)):
            if True:
                pass
        self.i = 0
        self.anim_timer = PyQt.QTimer(self.root)
        self.anim_timer.setInterval(1)
        self.anim_timer.timeout.connect(self.set_frame2)
        self.anim_timer.start()

    def set_frame2(self) -> None:
        x, z = self.rotate[self.i]
        entity = self.drone.entity
        if entity:
            transform = entity.findChild(PyQt.QTransform)
        current_pos = transform.translation()
        transform.setTranslation(current_pos + PyQt.QVector3D(x, 0, z))
        transform.setRotation(PyQt.QQuaternion.fromAxisAndAngle(
                        PyQt.QVector3D(0, 1, 0), -(self.i * 360 / 400)
                    ))
        self.i += 1
        if self.i == len(self.rotate):
            self.anim_timer.stop()
