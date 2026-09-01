import src.visual.PyQt6 as PyQt
from src.utils.graph import Graph
import math


class MapVisual():
    def __init__(self, root):
        self.root = root

    def create_maps(self, graph: Graph, drones=None):
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

    def make_grass(self, x_range: tuple[int, int], z_range: tuple[int, int]):
        middle_x = (x_range[0] + x_range[1]) / 2
        scale_x = (abs(x_range[0]) + abs(x_range[1])) + 20
        middle_z = (z_range[0] + z_range[1]) / 2
        scale_z = (abs(z_range[0]) + abs(z_range[1])) + 20

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
