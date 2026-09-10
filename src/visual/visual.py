import src.visual.PyQt6 as PyQt
from src.map_manager import MapsManager


class FileTree(PyQt.QTreeView):
    """
    Tree of all the maps availables
    """
    fileDoubleClicked = PyQt.Signal(str)

    def __init__(self, path: str) -> None:
        """
        Instantiate the FileTree, set the path to maps and activate
        maps loader on double click

        path -- path set as root of fileTree
        """
        super().__init__()

        self.file_model = PyQt.QFileSystemModel()
        self.file_model.setRootPath(path)

        self.setModel(self.file_model)

        self.setRootIndex(self.file_model.index(path))
        self.setStyleSheet("background-color: #222222")

        for column in range(1, 4):
            self.hideColumn(column)
        header = self.header()
        if header:
            header.hide()
        self.file_model.setNameFilters(["*.txt"])
        self.file_model.setNameFilterDisables(False)

        self.doubleClicked.connect(self._on_double_click)

    def _on_double_click(self, index: PyQt.QModelIndex) -> None:
        """Handle double click signal to load map"""
        path = self.file_model.filePath(index)

        if self.file_model.isDir(index):
            return

        self.fileDoubleClicked.emit(path)


class Delegating3DWindow(PyQt.Qt3DWindow):
    """
    3D Window that delegate event to the main window
    """
    def __init__(self, main_window: "MainWindow") -> None:
        """Instantiate reference to main window"""
        super().__init__()
        self.main_window = main_window

    def event(self, ev: PyQt.QEvent | None) -> bool:
        """Delegate all type of event to main window"""
        if not ev:
            return super().event(ev)
        if ev.type() in (
            PyQt.QEvent.Type.KeyPress,
            PyQt.QEvent.Type.KeyRelease,
            PyQt.QEvent.Type.MouseButtonPress,
            PyQt.QEvent.Type.MouseButtonRelease,
            PyQt.QEvent.Type.MouseMove,
            PyQt.QEvent.Type.Wheel,
        ):
            PyQt.QCoreApplication.sendEvent(self.main_window, ev)
            return True

        return super().event(ev)


class MainWindow(PyQt.QWidget):
    """
    Main window of the program, handle input and visual with GUI
    """
    turn_label: PyQt.QLabel

    def __init__(self) -> None:
        """
        Instantiate main window and all gui object such as 3d window,
        map manager, overlay and input frames
        """
        super().__init__()

        self.setFocusPolicy(PyQt.Qt.FocusPolicy.StrongFocus)
        self.setWindowTitle("Fly in")
        self.setMinimumSize(1200, 700)
        self.speed = 10

        self.root = PyQt.QEntity()
        self.view3d = Delegating3DWindow(self)
        bg = self.view3d.defaultFrameGraph()
        if bg:
            bg.setClearColor(PyQt.QColor("#222222"))

        self.view3d.setRootEntity(self.root)
        self.camera = self.view3d.camera()
        self.container = PyQt.QWidget.createWindowContainer(self.view3d, self)
        self.container.setFocusPolicy(PyQt.Qt.FocusPolicy.StrongFocus)
        self.container.setMouseTracking(True)

        self.setup_overlay()

        self.map_manager = MapsManager(self.root)

        self.keys: set[int] = set()

        self.move_time = PyQt.QTimer(self)
        self.move_time.setInterval(16)
        self.move_time.timeout.connect(self.process_camera_movement)
        self.move_time.start()

    def draw_map(self, filename: str) -> None:
        """Withdraw all elements of previous maps and create new one"""
        for child in self.root.children():
            child.setParent(None)
            child.deleteLater()
        if (not self.map_manager.create_maps(filename)
                or not self.map_manager.graph):
            return
        self.perspective = self.map_manager.graph.stats.min_z * -50 + 40
        self.setup_camera()
        self.setup_light()
        self.setup_turn()

    def setup_camera(self) -> None:
        """Define camera emplacement depending of map size"""
        if not self.camera or not self.map_manager.graph:
            return
        x = self.map_manager.graph.stats.middle_x
        z = self.map_manager.graph.stats.middle_z
        tmp = self.camera.lens()
        if tmp:
            tmp.setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1,
                                         1000.0)
        self.camera.setPosition(PyQt.QVector3D(x, x * 1.5,
                                               z + self.perspective))
        self.camera.setViewCenter(PyQt.QVector3D(x, 0.0, z))
        self.camera.setUpVector(PyQt.QVector3D(0.0, 0.0, -1.0))
        self.camera.setBottom(0)

    def setup_light(self) -> None:
        """Setup light source for the map"""
        if not self.map_manager.graph:
            return
        x = self.map_manager.graph.stats.middle_x
        self.light = PyQt.QEntity(self.root)

        light_pos = PyQt.QTransform()
        light_pos.setTranslation(PyQt.QVector3D(x, 200.0, 500))

        light = PyQt.QPointLight(self.light)
        light.setColor(PyQt.QColor("white"))
        light.setIntensity(1)

        self.light.addComponent(light)
        self.light.addComponent(light_pos)

    def setup_overlay(self) -> None:
        """Define Filetree and commands on overlay"""
        self.toolbar = PyQt.QVBoxLayout()

        self.file_tree = FileTree("maps/")
        self.file_tree.fileDoubleClicked.connect(self.draw_map)

        controls_label = PyQt.QLabel(
                    "<b>Q:</b> Quit simulation<br>"
                    "<b>WASD:</b> Move camera<br>"
                    "<b>Right Drag:</b> Look around<br>"
                    "<b>Scroll:</b> Zoom<br>"
                    "<b>Left / Right:</b> Change turn<br>"
                    "<b>R:</b> Run/Stop simulation<br>"
                    "<b>Up / Down:</b> Camera intensity<br>"
                    "<b>2:</b> 2D view<br>"
                    "<b>3:</b> 3D view",
                    self,
                )
        controls_label.setStyleSheet("font-size: 16px;")

        self.toolbar.addWidget(self.file_tree)
        self.toolbar.addWidget(controls_label)
        self.toolbar.addStretch()

        main_layout = PyQt.QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.addLayout(self.toolbar)
        main_layout.addWidget(self.container, stretch=1)

    def setup_turn(self) -> None:
        """Add to gui nb of turn that update on movement turn"""
        if not self.map_manager.graph:
            return
        if hasattr(self, "turn_label"):
            self.turn_label.setText(
                        f"<b>Turn {self.map_manager.visual.turn}/"
                        f"{self.map_manager.graph.stats.nb_turns}<b>"
                    )
        else:
            self.turn_label = PyQt.QLabel(
                        f"<b>Turn {self.map_manager.visual.turn}/"
                        f"{self.map_manager.graph.stats.nb_turns}<b>",
                        self
                    )
            self.toolbar.addWidget(self.turn_label)

    def update_turn(self) -> None:
        """Update turn on the gui"""
        if not self.map_manager.graph:
            return
        if hasattr(self, "turn_label"):
            self.turn_label.setText(
                        f"<b>Turn {self.map_manager.visual.turn}/"
                        f"{self.map_manager.graph.stats.nb_turns}<b>"
                    )

    def keyPressEvent(self, event: PyQt.QKeyEvent | None) -> None:
        """Handle key press event with personnalize event"""
        if event.key() == PyQt.Qt.Key.Key_Q:
            self.close()
        if not hasattr(self.map_manager, "graph"):
            return
        if not event:
            return
        match event.key():
            case PyQt.Qt.Key.Key_Right:
                self.map_manager.visual.change_turn(1)
                self.update_turn()
            case PyQt.Qt.Key.Key_Left:
                self.map_manager.visual.change_turn(-1)
                self.update_turn()
            case PyQt.Qt.Key.Key_Up:
                if self.speed > 6:
                    self.speed -= 2
            case PyQt.Qt.Key.Key_Down:
                if self.speed < 30:
                    self.speed += 3
            case PyQt.Qt.Key.Key_R:
                self.map_manager.visual.run = not self.map_manager.visual.run
                self.map_manager.visual.run_simulation()
            case PyQt.Qt.Key.Key_3:
                if self.map_manager.graph:
                    self.perspective = (self.map_manager.graph.stats.min_z
                                        * -50 + 40)
                self.setup_camera()
            case PyQt.Qt.Key.Key_2:
                self.perspective = 0
                self.setup_camera()
            case _:
                if not event.isAutoRepeat():
                    self.keys.add(event.key())
                super().keyPressEvent(event)

    def keyReleaseEvent(self, event: PyQt.QKeyEvent | None) -> None:
        """Handle key release event with personnalize event"""
        if not hasattr(self.map_manager, "graph"):
            return
        if not event:
            return
        if not event.isAutoRepeat():
            self.keys.discard(event.key())
        super().keyReleaseEvent(event)

    def wheelEvent(self, event: PyQt.QWheelEvent | None) -> None:
        """Handle wheel event as zoom for map"""
        if not hasattr(self.map_manager, "graph"):
            return
        if not self.camera or not self.map_manager.graph or not event:
            return
        delta = event.angleDelta().y()
        option = PyQt.QCamera.CameraTranslationOption.TranslateViewCenter
        x = self.map_manager.graph.stats.middle_x
        if delta > 0:
            self.camera.translate(PyQt.QVector3D(0, 0, x / self.speed), option)
        elif delta < 0:
            self.camera.translate(PyQt.QVector3D(0, 0, -x / self.speed),
                                  option)
        event.accept()

    def process_camera_movement(self) -> None:
        """Process camera movement update on key pressed"""
        if not hasattr(self.map_manager, "graph"):
            return
        if not self.keys or not self.camera or not self.map_manager.graph:
            return

        move_vector = PyQt.QVector3D(0, 0, 0)
        option = PyQt.QCamera.CameraTranslationOption.TranslateViewCenter
        x = self.map_manager.graph.stats.scale_x

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

    def mousePressEvent(self, event: PyQt.QMouseEvent | None) -> None:
        if not hasattr(self.map_manager, "graph"):
            return
        """Define mouse event as camera update"""
        if not event:
            return super().mouseMoveEvent(event)
        if event.button() == PyQt.Qt.MouseButton.LeftButton:
            self.last_mouse_pos = event.position()
        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event: PyQt.QMouseEvent | None) -> None:
        if not hasattr(self.map_manager, "graph"):
            return
        """Move camera according to mouse moving"""
        if not event or not self.camera:
            return super().mouseMoveEvent(event)
        if event.buttons() & PyQt.Qt.MouseButton.LeftButton:
            delta = event.position() - self.last_mouse_pos

            self.camera.pan(delta.x() * 0.2)
            self.camera.tilt(-delta.y() * 0.2)
            self.camera.setUpVector(PyQt.QVector3D(0.0, 1.0, 0.0))

            self.last_mouse_pos = event.position()
        return super().mouseMoveEvent(event)
