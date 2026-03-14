"""ProgressController — orchestrates start/stop/cancel and drives the progress bar."""

from __future__ import annotations

__all__ = ["ProgressController"]

from PySide6.QtCore import QObject, QTimer, Signal, Slot

from simple.views.main_window import MainWindow
from simple.views.progress_dialog import ProgressDialog

# Total duration in milliseconds (10 seconds)
_TOTAL_MS: int = 10_000
# Timer tick interval in milliseconds
_TICK_MS: int = 100


class ProgressController(QObject):
    """Coordinates the start/stop/cancel workflow between views.

    Owns the progress timer and updates the ProgressDialog at each tick.
    Emits ``progress_completed`` when the progress bar reaches 100%.

    Signals:
        progress_completed: Progress reached 100% naturally.
    """

    progress_completed: Signal = Signal()

    def __init__(self, window: MainWindow, dialog: ProgressDialog) -> None:
        super().__init__()
        self._window = window
        self._dialog = dialog
        self._elapsed_ms: int = 0

        self._timer = QTimer(self)
        self._timer.setInterval(_TICK_MS)
        self._timer.timeout.connect(self._on_timer_tick)

        self._window.start_requested.connect(self.on_start_requested)
        self._window.stop_requested.connect(self.on_stop_requested)
        self._dialog.cancelled.connect(self.on_cancelled)

    # ------------------------------------------------------------------
    # Public slots
    # ------------------------------------------------------------------

    @Slot()
    def on_start_requested(self) -> None:
        """Start the progress workflow."""
        self._elapsed_ms = 0
        self._dialog.reset()
        self._window.set_running(True)
        self._dialog.show()
        self._timer.start()

    @Slot()
    def on_stop_requested(self) -> None:
        """Stop the progress workflow (user clicked Stop)."""
        self._stop_workflow()

    @Slot()
    def on_cancelled(self) -> None:
        """Cancel the progress workflow (user clicked Cancel in dialog)."""
        self._stop_workflow()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @Slot()
    def _on_timer_tick(self) -> None:
        self._elapsed_ms += _TICK_MS
        progress = min(int(self._elapsed_ms * 100 / _TOTAL_MS), 100)
        self._dialog.set_progress(progress)
        if progress >= 100:
            self._finish_workflow()

    def _stop_workflow(self) -> None:
        """Halt the timer and return UI to idle state."""
        self._timer.stop()
        self._dialog.hide()
        self._window.set_running(False)

    def _finish_workflow(self) -> None:
        """Complete the workflow naturally at 100%."""
        self._timer.stop()
        self._dialog.hide()
        self._window.set_running(False)
        self.progress_completed.emit()
