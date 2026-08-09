from PyQt6.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow


class Window(QMainWindow):
    keyReleaseSignal = pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.label = QLabel("Press or release keys")
        self.setCentralWidget(self.label)

        self.keyReleaseSignal.connect(self.key_on_release)

    @pyqtSlot(int, int)
    def key_on_release(self, key, modifiers):
        print(f"Key release: {key}, modifiers: {modifiers}")

    def keyReleaseEvent(self, e):
        self.keyReleaseSignal.emit(e.key(), e.modifiers().value)
