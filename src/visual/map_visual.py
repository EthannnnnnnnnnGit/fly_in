import src.visual.PyQt6 as PyQt
from src.utils.graph import Graph
import math


class MapVisual():
    def __init__(self, root):
        self.root = root
        self.middle: tuple[int, int]
        self.max_size: int
        self.color = ["#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#00FFFF",
                      "#FF00FF", "#FFFFFF", "#000000", "#808080", "#FFA500"]

    def create_maps(self, graph: Graph, drones=None):
        self.graph = graph
        min_x, min_z, max_x, max_z = 0, 0, 0, 0
        for hub in graph.hubs.values():
            x, z = hub.coordinates
            z = -z
            min_x = x if x < min_x else min_x
            max_x = x if x > max_x else max_x
            min_z = z if z < min_z else min_z
            max_z = z if z > max_z else max_z
            self.create_hub((x * 15, z * 15), hub.color)
        for connection in graph.connections:
            x1, z1 = connection.hub1.coordinates
            x2, z2 = connection.hub2.coordinates
            self.create_river((x1 * 15, z1 * 15), (x2 * 15, z2 * 15))
        self.make_grass((min_x * 15, max_x * 15),
                        (min_z * 15, max_z * 15))
        self.create_drones()

    def make_grass(self, x_range: tuple[int, int], z_range: tuple[int, int]):
        middle_x = (x_range[0] + x_range[1]) / 2
        scale_x = (abs(x_range[0]) + abs(x_range[1])) + 20
        middle_z = (z_range[0] + z_range[1]) / 2
        scale_z = (abs(z_range[0]) + abs(z_range[1])) + 20
        self.middle = (middle_x, middle_z)
        self.max_size = max(scale_x - 20, scale_z - 20)

        grass = PyQt.QEntity(self.root)

        mesh = PyQt.QCuboidMesh()

        transform = PyQt.QTransform()
        transform.setTranslation(PyQt.QVector3D(middle_x, 0, middle_z))
        transform.setScale3D(PyQt.QVector3D(scale_x - 5, 1, scale_z - 5))

        material = PyQt.QPhongMaterial()
        material.setDiffuse(PyQt.QColor("#267001"))

        grass.addComponent(mesh)
        grass.addComponent(transform)
        grass.addComponent(material)

        dirt = PyQt.QEntity(self.root)

        mesh = PyQt.QCuboidMesh()

        transform = PyQt.QTransform()
        transform.setTranslation(PyQt.QVector3D(middle_x, -0.6, middle_z))
        transform.setScale3D(PyQt.QVector3D(scale_x, 1, scale_z))

        material = PyQt.QPhongMaterial()
        material.setDiffuse(PyQt.QColor("#63452C"))

        dirt.addComponent(mesh)
        dirt.addComponent(transform)
        dirt.addComponent(material)
        return (middle_x, middle_z)

    def create_hub(self, coordinates: tuple[float, float, float],
                   color: str):
        color = "blue" if not color else color
        x, z = coordinates
        y = 0.6
        scale = (5, 0.6, 5)

        hub = PyQt.QEntity(self.root)

        mesh = PyQt.QMesh()
        mesh.setSource(PyQt.QUrl.fromLocalFile("assets/lake.obj"))

        transform = PyQt.QTransform()
        transform.setTranslation(PyQt.QVector3D(x, y, z))
        transform.setScale3D(PyQt.QVector3D(*scale))

        material = PyQt.QPhongMaterial()
        material.setDiffuse(PyQt.QColor(color))

        hub.addComponent(mesh)
        hub.addComponent(transform)
        hub.addComponent(material)

    def create_river(self, start: tuple[int, int], end: tuple[int, int]):
        x1, z1 = start[0], -start[1]
        x2, z2 = end[0], -end[1]

        middle = ((x1 + x2) / 2, 0.6, (z1 + z2) / 2)
        angle = math.degrees(math.atan2(z2 - z1, x2 - x1))
        lenght = math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2)

        river = PyQt.QEntity(self.root)

        mesh = PyQt.QMesh()
        mesh.setSource(PyQt.QUrl.fromLocalFile("assets/water.obj"))

        transform = PyQt.QTransform()
        transform.setTranslation(PyQt.QVector3D(*middle))
        transform.setScale3D(PyQt.QVector3D(lenght, 0.5, 1))
        transform.setRotation(PyQt.QQuaternion.fromAxisAndAngle(
            PyQt.QVector3D(0, 1, 0), -angle
        ))

        material = PyQt.QPhongMaterial()
        material.setDiffuse(PyQt.QColor("blue"))

        river.addComponent(mesh)
        river.addComponent(transform)
        river.addComponent(material)

    def create_drones(self):
        self.turn = 0
        i = 1
        angle = 360 / len(self.graph.drones)
        x, z = self.graph.start.coordinates
        for i, drone in enumerate(self.graph.drones):
            drone.entity = PyQt.QEntity(self.root)

            mesh = PyQt.QMesh()
            mesh.setSource(PyQt.QUrl.fromLocalFile("assets/boat.obj"))

            transform = PyQt.QTransform()
            transform.setTranslation(PyQt.QVector3D(x, 2, z))
            transform.setRotation(PyQt.QQuaternion.fromAxisAndAngle(
                PyQt.QVector3D(0, 1, 0), i * angle
            ))

            material = PyQt.QPhongMaterial()
            material.setDiffuse(PyQt.QColor("#9D6C3C"))

            drone.entity.addComponent(mesh)
            drone.entity.addComponent(transform)
            drone.entity.addComponent(material)

    def change_turn(self, next_turn: int):
        drones_updates = []
        for drone in self.graph.drones:
            if (len(drone.hub_turns) <= self.turn + next_turn or
                len(drone.hub_turns) <= self.turn or
                    self.turn + next_turn < 0 or
                    (self.turn <= 0 and self.turn + next_turn <= 0)):
                continue
            if (drone.hub_turns[self.turn + next_turn] ==
                    drone.hub_turns[self.turn]):
                continue
            x1, z1 = drone.hub_turns[self.turn].coordinates
            x2, z2 = drone.hub_turns[self.turn + next_turn].coordinates
            vector = PyQt.QVector3D(x2 - x1, 0, -(z2 - z1))
            drones_updates.append((drone, vector))
        self.turn += next_turn

        self.current_step = 0
        self.anim_timer = PyQt.QTimer(self.root)
        self.anim_timer.setInterval(16)

        def set_frame():
            for drone, new_pos in drones_updates:
                transform = drone.entity.findChild(PyQt.QTransform)
                current_pos = transform.translation()
                transform.setTranslation(current_pos + new_pos)
            self.current_step += 1
            if self.current_step >= 15:
                self.anim_timer.stop()

        self.anim_timer.timeout.connect(set_frame)
        self.anim_timer.start()
