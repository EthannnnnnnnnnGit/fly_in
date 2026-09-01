import src.visual.PyQt6 as PyQt


class Window(PyQt.QWidget):
    keyReleaseSignal = PyQt.pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        self.label = PyQt.QLabel("Press or release keys")
        self.setCentralWidget(self.label)

        self.keyReleaseSignal.connect(self.key_on_release)

    @PyQt.pyqtSlot(int, int)
    def key_on_release(self, key, modifiers):
        print(f"Key release: {key}, modifiers: {modifiers}")

    def keyReleaseEvent(self, e):
        self.keyReleaseSignal.emit(e.key(), e.modifiers().value)
