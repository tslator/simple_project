"""Tests for the ProgressDialog view.

Tests follow pyqt_guidelines.md §6 — test behavior, not layout.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from simple.views.progress_dialog import ProgressDialog


@pytest.fixture()
def dialog(qtbot: QtBot) -> ProgressDialog:
    """Return a ProgressDialog registered for automatic cleanup."""
    d = ProgressDialog()
    qtbot.addWidget(d)
    return d


class TestInitialState:
    """Dialog starts with progress at 0."""

    def test_initial_progress_is_zero(self, dialog: ProgressDialog) -> None:
        assert dialog._ui.progressBar.value() == 0


class TestSetProgress:
    """set_progress() updates the progress bar value."""

    def test_set_progress_updates_bar(self, dialog: ProgressDialog) -> None:
        dialog.set_progress(42)
        assert dialog._ui.progressBar.value() == 42

    def test_set_progress_100(self, dialog: ProgressDialog) -> None:
        dialog.set_progress(100)
        assert dialog._ui.progressBar.value() == 100

    def test_set_progress_clamps_high(self, dialog: ProgressDialog) -> None:
        """QProgressBar ignores values above its maximum; value stays at previous."""
        dialog.set_progress(50)
        dialog.set_progress(200)
        # PySide6 QProgressBar silently ignores out-of-range values
        assert dialog._ui.progressBar.value() == 50


class TestReset:
    """reset() returns the progress bar to 0."""

    def test_reset_returns_to_zero(self, dialog: ProgressDialog) -> None:
        dialog.set_progress(75)
        dialog.reset()
        assert dialog._ui.progressBar.value() == 0


class TestCancelSignal:
    """Cancel button emits the cancelled signal (F-09)."""

    def test_cancel_emits_cancelled(self, dialog: ProgressDialog, qtbot: QtBot) -> None:
        dialog.show()
        with qtbot.waitSignal(dialog.cancelled, timeout=1000):
            qtbot.mouseClick(dialog._ui.cancelButton, Qt.MouseButton.LeftButton)
