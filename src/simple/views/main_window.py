"""MainWindow view for the simple application."""

from __future__ import annotations

__all__ = ["MainWindow"]

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QMainWindow

from simple.generated.ui_main_window import Ui_MainWindow


class MainWindow(QMainWindow):
    """Main application window.

    Emits:
        start_requested: User clicked the Start button.
        stop_requested:  User clicked the Stop button.
    """

    start_requested: Signal = Signal()
    stop_requested: Signal = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        self._connect_signals()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def set_running(self, running: bool) -> None:
        """Enable/disable Start and Stop buttons based on the running state."""
        self._ui.startButton.setEnabled(not running)
        self._ui.stopButton.setEnabled(running)

    # ------------------------------------------------------------------
    # Private slots
    # ------------------------------------------------------------------

    def _connect_signals(self) -> None:
        self._ui.startButton.clicked.connect(self._on_startButton_clicked)
        self._ui.stopButton.clicked.connect(self._on_stopButton_clicked)

    @Slot()
    def _on_startButton_clicked(self) -> None:
        self.start_requested.emit()

    @Slot()
    def _on_stopButton_clicked(self) -> None:
        self.stop_requested.emit()
