import src.visual.PyQt6 as PyQt
from src.map_manager import MapsManager
from src.visual.file import RestrictedDirFile
import os


class Delegating3DWindow(PyQt.Qt3DWindow):

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def event(self, ev) -> bool:
        # Pass key, mouse, and wheel events directly to MainWindow
        if ev.type() in (
            PyQt.QEvent.Type.KeyPress,
            PyQt.QEvent.Type.KeyRelease,
            PyQt.QEvent.Type.MouseButtonPress,
            PyQt.QEvent.Type.MouseButtonRelease,
            PyQt.QEvent.Type.MouseMove,
            PyQt.QEvent.Type.Wheel,
        ):
            # Send event to MainWindow's handler
            PyQt.QCoreApplication.sendEvent(self.main_window, ev)
            return True

        return super().event(ev)


class MainWindow(PyQt.QWidget):
    def __init__(self) -> None:
        super().__init__()

        # initialize main window
        self.setFocusPolicy(PyQt.Qt.FocusPolicy.StrongFocus)
        self.setWindowTitle("Fly in")
        self.setMinimumSize(1000, 700)

        self.root = PyQt.QEntity()
        # initialize 3d window and add to main window
        self.view3d = Delegating3DWindow(self)
        self.view3d.defaultFrameGraph().setClearColor(PyQt.QColor("white"))

        self.view3d.setRootEntity(self.root)
        self.camera = self.view3d.camera()
        self.container = PyQt.QWidget.createWindowContainer(self.view3d, self)
        self.container.setFocusPolicy(PyQt.Qt.FocusPolicy.StrongFocus)
        self.container.setMouseTracking(True)

        self.setup_overlay()

        self.map_manager = MapsManager(self.root)

        self.keys = set()

        self.move_time = PyQt.QTimer(self)
        self.move_time.setInterval(16)
        self.move_time.timeout.connect(self.process_camera_movement)
        self.move_time.start()

    def draw_map(self, filename: str):
        for child in self.root.children():
            child.setParent(None)
            child.deleteLater()
        self.map_manager.create_maps(filename)
        self.setup_camera()
        self.setup_light()

    def setup_camera(self) -> None:
        x, z = self.map_manager.visual.middle
        self.camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1,
                                                    1000.0)
        self.camera.setPosition(PyQt.QVector3D(x, 50, z))
        self.camera.setViewCenter(PyQt.QVector3D(x, 0.0, z))
        self.camera.setUpVector(PyQt.QVector3D(0.0, 0.0, -1.0))
        self.camera.setBottom(0)

        # self.cam_controll = PyQt.QFirstPersonCameraController(self.root)
        # self.cam_controll.setCamera(camera)
        # self.cam_controll.setLinearSpeed(200.0)

    def setup_light(self):
        x, z = self.map_manager.visual.middle
        self.light = PyQt.QEntity(self.root)

        light_pos = PyQt.QTransform()
        light_pos.setTranslation(PyQt.QVector3D(x, 200.0, 500))

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

    def keyPressEvent(self, event):
        match event.key():
            case PyQt.Qt.Key.Key_Q:
                self.close()
            case PyQt.Qt.Key.Key_Right:
                self.map_manager.visual.change_turn(1)
            case PyQt.Qt.Key.Key_Left:
                self.map_manager.visual.change_turn(-1)
            case _:
                if not event.isAutoRepeat():
                    self.keys.add(event.key())
                super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            self.keys.discard(event.key())
        super().keyReleaseEvent(event)

    def wheelEvent(self, event: PyQt.QWheelEvent):
        return super().wheelEvent(event)

    def process_camera_movement(self):
        if not self.keys:
            return

        speed = 0.5
        move_vector = PyQt.QVector3D(0, 0, 0)
        option = PyQt.QCamera.CameraTranslationOption.TranslateViewCenter

        if PyQt.Qt.Key.Key_W in self.keys:
            move_vector += PyQt.QVector3D(0, speed, 0)
        if PyQt.Qt.Key.Key_S in self.keys:
            move_vector += PyQt.QVector3D(0, -speed, 0)
        if PyQt.Qt.Key.Key_A in self.keys:
            move_vector += PyQt.QVector3D(-speed, 0, 0)
        if PyQt.Qt.Key.Key_D in self.keys:
            move_vector += PyQt.QVector3D(speed, 0, 0)

        if not move_vector.isNull():
            self.camera.translate(move_vector, option)
