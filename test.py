from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6.QtCore import QSize, Qt
import sys


app = QApplication(sys.argv)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        button = QPushButton("Press Me!")
        self.setMinimumSize(QSize(200, 150))
        self.setMaximumSize(QSize(1000, 800))

        # Set the central widget of the Window.
        self.setCentralWidget(button)


window = MainWindow()
window.show()

app.exec()
