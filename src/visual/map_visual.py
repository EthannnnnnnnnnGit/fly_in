import src.visual.PyQt6 as PyQt
from src.utils.graph import Graph
from src.utils.connection import Connection
from src.utils.hub import Hub
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
        if not hasattr(self, "sim_timer"):
            self.sim_timer = PyQt.QTimer(self.root)
            self.sim_timer.timeout.connect(self._step_simulation)

        self.sim_timer.start(500)

    def _step_simulation(self) -> None:
        if self.turn == self.graph.stats.nb_turns or not self.run:
            self.sim_timer.stop()
            return

        if not self.is_processing:
            self.change_turn(1)

    def stop_simulation(self) -> None:
        if hasattr(self, "sim_timer"):
            self.sim_timer.stop()

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
            print(vector, goal_vector)
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
        if stop:
            self.anim_timer.stop()
            self.is_processing = False

    def rotate_hub(self) -> None:
        if hasattr(self, "anim_timer") and not isdeleted(self.anim_timer):
            if self.anim_timer.isActive():
                self.anim_timer.stop()
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


class OrbitHub():
    def __init__(self, buoy: PyQt.QVector3D):
        self.center = buoy
        self.radius = 6
        self.current_angle = 0
        self.speed = 0.03

    def get_next_orbit_pos(self) -> PyQt.QVector3D:
        self.current_angle += self.speed

        if self.current_angle > 2 * math.pi:
            self.current_angle -= 2 * math.pi

        x = self.center.x() + self.radius() + math.cos(self.current_angle)
        z = self.center.z() + self.radius() + math.sin(self.current_angle)

        return PyQt.QVector3D(x, self.center.y(), z)

    def calculate_heading_angle(self, current_pos: PyQt.QVector3D,
                                target_pos: PyQt.QVector3D) -> float:
        """Calculates the rotation angle in degrees on the XZ plane."""
        direction = target_pos - current_pos
        angle_rad = math.atan2(direction.z(), direction.x())
        return math.degrees(angle_rad)

    def set_boat_rotation(self, boat_entity, current_pos: PyQt.QVector3D,
                          target_pos: PyQt.QVector3D, model_offset: float = 90.0) -> None:
        """Rotates the boat's QTransform to face toward target_pos."""
        angle_deg = self.calculate_heading_angle(current_pos, target_pos)
        final_angle = angle_deg + model_offset
        rotation = PyQt.QQuaternion.fromAxisAndAngle(PyQt.QVector3D(0, 1, 0), -final_angle)
        boat_entity.transform.setRotation(rotation)

    def update_boat_movement(self, boat, speed: float = 0.1,
                             arrival_threshold: float = 0.2) -> None:
        """Call this inside your QTimer tick / frame update loop."""
        if not boat.has_active_path():
            return

        current_pos = boat.position
        target_pos = boat.current_waypoint()

        # Calculate distance to current target coordinate
        distance = current_pos.distanceToPoint(target_pos)

        if distance <= arrival_threshold:
            # 1. Snap directly to the exact destination coordinate
            boat.set_position(target_pos)

            # 2. Advance to next point in the orbit/route
            boat.advance_waypoint()

            # 3. If there is a next point, rotate immediately toward it (or the final connection)
            if boat.has_active_path():
                next_target = boat.current_waypoint()
                set_boat_rotation(boat, target_pos, next_target)
            else:
                # Reached final node: align with the connection path vector
                set_boat_rotation(boat, target_pos, boat.connection_target_pos)
        else:
            # 1. Face the target coordinate while moving
            set_boat_rotation(boat, current_pos, target_pos)

            # 2. Move step towards target coordinate
            direction = (target_pos - current_pos).normalized()
            new_pos = current_pos + (direction * speed)
            boat.set_position(new_pos)
