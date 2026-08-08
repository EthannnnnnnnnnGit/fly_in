from src.visual import *
import sys


class MainWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # initialize main window
        self.setWindowTitle("Fly in")
        self.setMinimumSize(1000, 700)

        # initialize 3d window and add to main window
        self.view3d = Qt3DWindow()
        self.view3d.defaultFrameGraph().setClearColor(QColor("#39AABB"))

        self.root = QEntity()
        self.view3d.setRootEntity(self.root)
        self.container = QWidget.createWindowContainer(self.view3d, self)

        self.setup_camera()
        self.setup_light()
        self.setup_overlay()

    def setup_camera(self) -> None:
        camera = self.view3d.camera()
        camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
        camera.setPosition(QVector3D(0.0, 20.0, 40.0))
        camera.setViewCenter(QVector3D(0.0, 0.0, 0.0))

        self.cam_controll = QFirstPersonCameraController(self.root)
        self.cam_controll.setCamera(camera)

    def setup_light(self):
        self.light = QEntity(self.root)
        light = QPointLight(self.light)
        light.setColor(QColor("#EFDD10"))
        light.setIntensity(1.5)
        self.light.addComponent(light)

    def setup_overlay(self):
        self.overlay = QWidget(self)
        self.overlay.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        overlay_box = QHBoxLayout()
        overlay_box.setContentsMargins(20, 20, 20, 20)

        top = QHBoxLayout()
        top.addStretch()

        self.button_file = QPushButton("Select a map")
        self.button_file.setCursor(Qt.CursorShape.PointingHandCursor)
        self.button_file.setStyleSheet("""
            QPushButton {
                background-color: #1e1e2e;
                color: #000000;
                border: 2px solid #89b4fa;
                border-radius: 8px;
                padding: 10px 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #89b4fa;
                color: #11111b;
            }
        """)
        top.addWidget(self.button_file)
        overlay_box.addLayout(top)
        overlay_box.addStretch()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        width, height = self.width(), self.height()

        self.container.setGeometry(0, 0, width, height)
        self.overlay.setGeometry(0, 0, width, height)

        # Keep 3D aspect ratio updated
        if height > 0:
            self.view3d.camera().lens().setAspectRatio(width / height)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
