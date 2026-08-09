from PyQt6.QtWidgets import QFileDialog, QWidget
import os


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
