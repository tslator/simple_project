"""Application entry point."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from simple.controllers.progress_controller import ProgressController
from simple.views.main_window import MainWindow
from simple.views.progress_dialog import ProgressDialog


def main() -> None:
    """Create the QApplication, wire up views and controller, and run."""
    app = QApplication(sys.argv)

    window = MainWindow()
    dialog = ProgressDialog(window)
    _controller = ProgressController(window, dialog)  # noqa: F841 — kept alive

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
