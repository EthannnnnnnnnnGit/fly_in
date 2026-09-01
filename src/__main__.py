from src.visual.visual import MainWindow
import src.visual.PyQt6 as PyQt


def main() -> None:
    app = PyQt.QApplication([])

    window = MainWindow()
    window.show()

    app.exec()


if __name__ == "__main__":
    main()
