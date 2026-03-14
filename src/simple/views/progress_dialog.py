"""ProgressDialog view for the simple application."""

from __future__ import annotations

__all__ = ["ProgressDialog"]

from PySide6.QtCore import Signal, Slot
from PySide6.QtWidgets import QDialog, QWidget

from simple.generated.ui_progress_dialog import Ui_ProgressDialog


class ProgressDialog(QDialog):
    """Non-modal progress dialog.

    Emits:
        cancelled: User clicked the Cancel button.
    """

    cancelled: Signal = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._ui = Ui_ProgressDialog()
        self._ui.setupUi(self)
        self._ui.cancelButton.clicked.connect(self._on_cancelButton_clicked)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def set_progress(self, value: int) -> None:
        """Set the progress bar to *value* (0–100)."""
        self._ui.progressBar.setValue(value)

    def reset(self) -> None:
        """Reset progress bar to 0."""
        self._ui.progressBar.setValue(0)

    # ------------------------------------------------------------------
    # Private slots
    # ------------------------------------------------------------------

    @Slot()
    def _on_cancelButton_clicked(self) -> None:
        self.cancelled.emit()
