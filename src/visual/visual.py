import src.visual.PyQt6 as PyQt
from src.map_manager import MapsManager
from src.visual.file import RestrictedDirFile
import os


class FileTree(PyQt.QTreeView):
    fileDoubleClicked = PyQt.Signal(str)

    def __init__(self, path: str):
        super().__init__()

        self.file_model = PyQt.QFileSystemModel()
        self.file_model.setRootPath(path)

        self.setModel(self.file_model)

        self.setRootIndex(self.file_model.index(path))

        for column in range(1, 4):
            self.hideColumn(column)
        self.header().hide()
        self.file_model.setNameFilters(["*.txt"])
        self.file_model.setNameFilterDisables(False)

        self.doubleClicked.connect(self._on_double_click)

    def _on_double_click(self, index: PyQt.QModelIndex):
        path = self.file_model.filePath(index)

        if self.file_model.isDir(index):
            return

        self.fileDoubleClicked.emit(path)


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
        self.speed = 10

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
        self.draw_map("maps/easy/01_linear_path.txt")

        self.keys = set()

        self.move_time = PyQt.QTimer(self)
        self.move_time.setInterval(16)
        self.move_time.timeout.connect(self.process_camera_movement)
        self.move_time.start()

    def draw_map(self, filename: str):
        for child in self.root.children():
            child.setParent(None)
            child.deleteLater()
        if (not self.map_manager.create_maps(filename)):
            return
        self.setup_camera()
        self.setup_light()

    def setup_camera(self) -> None:
        x, z = self.map_manager.visual.middle
        self.camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1,
                                                    1000.0)
        self.camera.setPosition(PyQt.QVector3D(x, x * 2, z))
        self.camera.setViewCenter(PyQt.QVector3D(x, 0.0, z))
        self.camera.setUpVector(PyQt.QVector3D(0.0, 0.0, -1.0))
        self.camera.setBottom(0)

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
        toolbar = PyQt.QVBoxLayout()

        self.file_tree = FileTree("maps/")
        self.file_tree.fileDoubleClicked.connect(self.draw_map)

        toolbar.addWidget(self.file_tree)
        toolbar.addStretch()

        main_layout = PyQt.QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addLayout(toolbar)
        main_layout.addWidget(self.container, stretch=1)

    def keyPressEvent(self, event):
        match event.key():
            case PyQt.Qt.Key.Key_Q:
                self.close()
            case PyQt.Qt.Key.Key_Right:
                self.map_manager.visual.change_turn(1)
            case PyQt.Qt.Key.Key_Left:
                self.map_manager.visual.change_turn(-1)
            case PyQt.Qt.Key.Key_T:
                self.map_manager.visual.tourner_dans_le_vide()
            case PyQt.Qt.Key.Key_R:
                self.setup_camera()
            case _:
                if not event.isAutoRepeat():
                    self.keys.add(event.key())
                super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if not event.isAutoRepeat():
            self.keys.discard(event.key())
        super().keyReleaseEvent(event)

    def wheelEvent(self, event: PyQt.QWheelEvent):
        delta = event.angleDelta().y()
        option = PyQt.QCamera.CameraTranslationOption.TranslateViewCenter
        x, _ = self.map_manager.visual.middle
        if delta > 0:
            self.camera.translate(PyQt.QVector3D(0, 0, x / self.speed), option)
        elif delta < 0:
            self.camera.translate(PyQt.QVector3D(0, 0, -x / self.speed),
                                  option)
        event.accept()

    def process_camera_movement(self):
        if not self.keys:
            return

        move_vector = PyQt.QVector3D(0, 0, 0)
        option = PyQt.QCamera.CameraTranslationOption.TranslateViewCenter
        x, _ = self.map_manager.visual.middle

        if PyQt.Qt.Key.Key_W in self.keys:
            move_vector += PyQt.QVector3D(0, x / (self.speed * 4), 0)
        if PyQt.Qt.Key.Key_S in self.keys:
            move_vector += PyQt.QVector3D(0, -x / (self.speed * 4), 0)
        if PyQt.Qt.Key.Key_A in self.keys:
            move_vector += PyQt.QVector3D(-x / (self.speed * 4), 0, 0)
        if PyQt.Qt.Key.Key_D in self.keys:
            move_vector += PyQt.QVector3D(x / (self.speed * 4), 0, 0)
        if not move_vector.isNull():
            self.camera.translate(move_vector, option)

    def mousePressEvent(self, event):
        if event.button() == PyQt.Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.position()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & PyQt.Qt.MouseButton.LeftButton:
            delta = event.position() - self.last_mouse_pos

            self.camera.pan(delta.x() * 0.2)
            self.camera.tilt(-delta.y() * 0.2)
            self.camera.setUpVector(PyQt.QVector3D(0.0, 1.0, 0.0))

            self.last_mouse_pos = event.position()
        return super().mouseMoveEvent(event)
