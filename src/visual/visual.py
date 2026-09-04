import src.visual.PyQt6 as PyQt
from src.map_manager import MapsManager
from src.visual.file import RestrictedDirFile
import os


class MainWindow(PyQt.QWidget):
    def __init__(self) -> None:
        super().__init__()

        # initialize main window
        self.setWindowTitle("Fly in")
        self.setMinimumSize(1000, 700)

        self.root = PyQt.QEntity()
        # initialize 3d window and add to main window
        self.view3d = PyQt.Qt3DWindow()
        self.view3d.defaultFrameGraph().setClearColor(PyQt.QColor("white"))

        self.view3d.setRootEntity(self.root)
        self.container = PyQt.QWidget.createWindowContainer(self.view3d, self)

        self.setup_overlay()

        self.map_manager = MapsManager(self.root)

    def draw_map(self, filename: str):
        for child in self.root.children():
            child.setParent(None)
            child.deleteLater()
        self.setup_camera()
        self.setup_light()
        self.map_manager.create_maps(filename)

    def setup_camera(self) -> None:
        camera = self.view3d.camera()
        camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        camera.setPosition(PyQt.QVector3D(0.0, 20.0, 40.0))
        camera.setViewCenter(PyQt.QVector3D(0.0, 0.0, 0.0))
        camera.setBottom(0)

        self.cam_controll = PyQt.QFirstPersonCameraController(self.root)
        self.cam_controll.setCamera(camera)
        self.cam_controll.setLinearSpeed(40.0)

    def setup_light(self):
        self.light = PyQt.QEntity(self.root)

        light_pos = PyQt.QTransform()
        light_pos.setTranslation(PyQt.QVector3D(0.0, 50.0, 50.0))

        light = PyQt.QPointLight(self.light)
        light.setColor(PyQt.QColor("white"))
        light.setIntensity(1)

        self.light.addComponent(light)
        self.light.addComponent(light_pos)

    def setup_overlay(self):
        toolbar = PyQt.QHBoxLayout()
        self.button_file = PyQt.QPushButton("Select a map")
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

        main_layout = PyQt.QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addLayout(toolbar)
        main_layout.addWidget(self.container, stretch=1)

    def open_file_dialog(self) -> None:
        target_maps_folder = os.path.join(os.getcwd(), "maps")

        dialog = RestrictedDirFile(self, target_maps_folder)

        if dialog.exec() == PyQt.QFileDialog.DialogCode.Accepted:
            selected_file = dialog.selectedFiles()[0]
            if selected_file:
                self.draw_map(selected_file)
