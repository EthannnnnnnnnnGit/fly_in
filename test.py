from src.visual.PyQt6 import *
import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QFileDialog
from src.visual.file import RestrictedDirFile
import os
from pathlib import Path
from PyQt6.Qt3DExtras import QCuboidMesh


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
        self.hub_creator.create_hub((-15.0, 0.0, 0.0), "#a6e3a1")
        self.hub_creator.create_hub((0.0, 0.0, -10.0), "#89b4fa")
        self.hub_creator.create_hub((0.0, 0.0, 10.0), "#cba6f7")
        self.hub_creator.create_hub((15.0, 0.0, 0.0), "#f38ba8")

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
        light = QPointLight(self.light)
        light.setColor(QColor("#EFDD10"))
        light.setIntensity(1)
        self.light.addComponent(light)

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

    def create_hub(self, coordinates: tuple[float, float, float], color: str):
        hub = QEntity(self.root)

        mesh = QCuboidMesh()

        transform = QTransform()
        transform.setTranslation(QVector3D(*coordinates))

        material = QPhongMaterial()
        material.setDiffuse(QColor(color))

        hub.addComponent(mesh)
        hub.addComponent(transform)
        hub.addComponent(material)

        return hub


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenetre = MainWindow()
    fenetre.show()
    app.exec()
