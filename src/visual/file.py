from PyQt6.QtWidgets import QFileDialog, QWidget
import os
# from pathlib import Path


# class Window(QWidget):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)

#         self.setWindowTitle('PyQt File Dialog')
#         self.setGeometry(100, 100, 400, 100)

#         layout = QGridLayout()
#         self.setLayout(layout)

#         # file selection
#         file_browse = QPushButton('Browse')
#         file_browse.clicked.connect(self.open_file_dialog)
#         self.filename_edit = QLineEdit()

#         layout.addWidget(QLabel('File:'), 0, 0)
#         layout.addWidget(self.filename_edit, 0, 1)
#         layout.addWidget(file_browse, 0, 2)

#         self.show()

#     def open_file_dialog(self) -> None:
#         target_maps_folder = os.path.join(os.getcwd(), "maps")

#         dialog = RestrictedDirFile(self, target_maps_folder)

#         if dialog.exec() == QFileDialog.DialogCode.Accepted:
#             selected_files = dialog.selectedFiles()[0]
#             if selected_files:
#                 path = Path(selected_files)
#                 self.filename_edit.setText(str(path))

class RestrictedDirFile(QFileDialog):
    def __init__(self, parent: QWidget, maps_dir: str):
        super().__init__(parent, "Select a file")
        self.maps_dir: str = os.path.abspath(maps_dir)
        self.setDirectory(self.maps_dir)
        self.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        self.setSidebarUrls([])
        self.setOption(QFileDialog.Option.ReadOnly, True)
        self.directoryEntered.connect(self.force_maps_dir)

    def force_maps_dir(self, new_dir: str) -> None:
        """Enforces that the user stays inside maps_dir or its subfolders."""
        abs_new_dir = os.path.abspath(new_dir)

        # Check if the requested folder starts with our designated maps path
        if not abs_new_dir.startswith(self.maps_dir):
            # Reset view back to the allowed root directory immediately
            self.setDirectory(self.maps_dir)
