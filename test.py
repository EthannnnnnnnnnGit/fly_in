from src.visual.PyQt6 import *
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog
from src.visual.file import RestrictedDirFile
import os
from pathlib import Path
from PyQt6.Qt3DExtras import QCuboidMesh
from PyQt6.QtGui import QQuaternion
from PyQt6.Qt3DRender import QSceneLoader, QMesh, QRenderStateSet, QDepthTest, QColorMask
from PyQt6.QtCore import QUrl
import math


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # initialize main window
        self.setWindowTitle("Fly in")
        # self.setStyleSheet("background-color: #ffffff")
        self.setMinimumSize(1000, 700)

        self.root = QEntity()
        # initialize 3d window and add to main window
        self.view3d = Qt3DWindow()
        self.view3d.defaultFrameGraph().setClearColor(QColor("white"))

        self.view3d.setRootEntity(self.root)
        self.container = QWidget.createWindowContainer(self.view3d, self)

        self.setup_camera()
        self.setup_light()
        self.setup_overlay()

        self.hub_creator = HubsVisualizer(self.root)
        self.hub_creator.create_maps()

    def setup_camera(self) -> None:
        camera = self.view3d.camera()
        camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        camera.setPosition(QVector3D(0.0, 20.0, 40.0))
        camera.setViewCenter(QVector3D(0.0, 0.0, 0.0))
        camera.setBottom(0)

        self.cam_controll = QFirstPersonCameraController(self.root)
        self.cam_controll.setCamera(camera)
        self.cam_controll.setLinearSpeed(40.0)

    def setup_light(self):
        self.light = QEntity(self.root)

        light_pos = QTransform()
        light_pos.setTranslation(QVector3D(0.0, 50.0, 50.0))

        light = QPointLight(self.light)
        light.setColor(QColor("white"))
        light.setIntensity(1)

        self.light.addComponent(light)
        self.light.addComponent(light_pos)

    def setup_overlay(self):
        toolbar = QHBoxLayout()
        self.button_file = QPushButton("Select a map")
        self.button_file.clicked.connect(self.open_file_dialog)
        self.button_file.setStyleSheet("""
            QPushButton {
                background-color: #000000;
                color: #ffffff;
                border: 2px solid #89b4fa;
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #89b4fa;
                color: #000000;
            }
        """)
        toolbar.addWidget(self.button_file)
        toolbar.addStretch()

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addLayout(toolbar)
        main_layout.addWidget(self.container, stretch=1)

    def open_file_dialog(self) -> None:
        target_maps_folder = os.path.join(os.getcwd(), "maps")

        dialog = RestrictedDirFile(self, target_maps_folder)

        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = dialog.selectedFiles()[0]
            if selected_files:
                self.path = Path(selected_files)


class HubsVisualizer():
    def __init__(self, root):
        self.root = root
        self.define_grass_check()
        self.define_water_check()

    def create_maps(self):
        data = [((0, 0), (15, 5)),
                ((15, 5), (30, 0)),
                ((0, 0), (15, -5)),
                ((15, -5), (30, 0))]
        for coordinate in data:
            self.create_river(coordinate[0], coordinate[1])
        self.create_hub((0, 0))
        self.create_hub((15, 5))
        self.create_hub((15, -5))
        self.create_hub((30, 0))
        self.make_grass()

    def make_grass(self):
        for x, z in [(x, z) for x in range(-5, 35) for z in range(-10, 10)]:
            grass = QEntity(self.root)

            mesh = QMesh()
            mesh.setSource(QUrl.fromLocalFile("assets/grass.obj"))

            transform = QTransform()
            transform.setTranslation(QVector3D(x, 0, z))

            grass.addComponent(mesh)
            grass.addComponent(transform)
            grass.addComponent(self.grass_check)

    def create_hub(self, coordinates: tuple[float, float, float], color: str = "blue"):
        hub = QEntity(self.root)
        x, z = coordinates
        y = -0.4
        scale = (5, 1, 5)

        mesh = QMesh()
        mesh.setSource(QUrl.fromLocalFile("assets/lake.obj"))

        transform = QTransform()
        transform.setTranslation(QVector3D(x, y, z))
        transform.setScale3D(QVector3D(*scale))

        material = QPhongMaterial()
        material.setDiffuse(QColor("blue"))

        hub.addComponent(mesh)
        hub.addComponent(transform)
        hub.addComponent(material)

        self.apply_mask((x, y + 0.1, z), (5, 2, 5), mesh)

    def create_river(self, start: tuple[int, int], end: tuple[int, int]):
        x1, z1 = start[0], -start[1]
        x2, z2 = end[0], -end[1]

        middle = ((x1 + x2) / 2, 0, (z1 + z2) / 2)
        angle = math.degrees(math.atan2(z2 - z1, x2 - x1))
        lenght = math.sqrt((x2 - x1) ** 2 + (z2 - z1) ** 2)

        river = QEntity(self.root)

        mesh = QMesh()
        mesh.setSource(QUrl.fromLocalFile("assets/water.obj"))

        transform = QTransform()
        transform.setTranslation(QVector3D(*middle))
        transform.setScale3D(QVector3D(lenght, 0.5, 1))
        transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(0, 1, 0), -angle))

        material = QPhongMaterial()
        material.setDiffuse(QColor("blue"))

        river.addComponent(mesh)
        river.addComponent(transform)
        river.addComponent(material)

        self.apply_mask(middle, (lenght, 1.3, 1), mesh, angle)

    def apply_mask(self, coordinates, scale, mesh: QMesh, angle: int = 0):
        mask = QEntity(self.root)

        transform = QTransform()
        transform.setTranslation(QVector3D(*coordinates))
        transform.setScale3D(QVector3D(*scale))
        transform.setRotation(QQuaternion.fromAxisAndAngle(QVector3D(0, 1, 0), -angle))

        mask.addComponent(mesh)
        mask.addComponent(transform)
        mask.addComponent(self.mask_check)

    def define_water_check(self):
        self.mask_check = QPhongMaterial()

        mask_color = QColorMask()
        mask_color.setRedMasked(False)
        mask_color.setGreenMasked(False)
        mask_color.setBlueMasked(False)
        mask_color.setAlphaMasked(False)

        mask_depth = QDepthTest()
        mask_depth.setDepthFunction(QDepthTest.DepthFunction.Less)

        for technique in self.mask_check.effect().techniques():
            for render_pass in technique.renderPasses():
                render_pass.addRenderState(mask_color)
                render_pass.addRenderState(mask_depth)

    def define_grass_check(self):
        self.grass_check = QPhongMaterial()
        self.grass_check.setDiffuse(QColor("#267001"))

        grass_depth = QDepthTest()
        grass_depth.setDepthFunction(QDepthTest.DepthFunction.LessOrEqual)

        for technique in self.grass_check.effect().techniques():
            for render_pass in technique.renderPasses():
                render_pass.addRenderState(grass_depth)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = MainWindow()
    fenetre.show()
    app.exec()
