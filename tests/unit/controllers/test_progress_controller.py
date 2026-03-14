"""Tests for the ProgressController.

Tests follow pyqt_guidelines.md §6 — test behavior, not layout.
"""

from __future__ import annotations

import pytest
from pytestqt.qtbot import QtBot

from simple.controllers.progress_controller import ProgressController
from simple.views.main_window import MainWindow
from simple.views.progress_dialog import ProgressDialog


@pytest.fixture()
def window(qtbot: QtBot) -> MainWindow:
    """Return a MainWindow registered for automatic cleanup."""
    w = MainWindow()
    qtbot.addWidget(w)
    return w


@pytest.fixture()
def dialog(qtbot: QtBot, window: MainWindow) -> ProgressDialog:
    """Return a ProgressDialog registered for automatic cleanup."""
    d = ProgressDialog(window)
    qtbot.addWidget(d)
    return d


@pytest.fixture()
def controller(window: MainWindow, dialog: ProgressDialog) -> ProgressController:
    """Return a ProgressController wired to the fixtures."""
    return ProgressController(window, dialog)


class TestStartWorkflow:
    """F-01 through F-04: starting the workflow."""

    def test_start_shows_dialog(
        self, controller: ProgressController, window: MainWindow, dialog: ProgressDialog
    ) -> None:
        window.start_requested.emit()
        assert dialog.isVisible()

    def test_start_disables_start_button(
        self, controller: ProgressController, window: MainWindow
    ) -> None:
        window.start_requested.emit()
        assert not window._ui.startButton.isEnabled()

    def test_start_enables_stop_button(
        self, controller: ProgressController, window: MainWindow
    ) -> None:
        window.start_requested.emit()
        assert window._ui.stopButton.isEnabled()

    def test_start_resets_progress_to_zero(
        self,
        controller: ProgressController,
        window: MainWindow,
        dialog: ProgressDialog,
    ) -> None:
        dialog.set_progress(50)
        window.start_requested.emit()
        assert dialog._ui.progressBar.value() == 0


class TestStopWorkflow:
    """F-07 and F-08: stopping the workflow."""

    def test_stop_hides_dialog(
        self,
        controller: ProgressController,
        window: MainWindow,
        dialog: ProgressDialog,
    ) -> None:
        window.start_requested.emit()
        window.stop_requested.emit()
        assert not dialog.isVisible()

    def test_stop_enables_start_button(
        self, controller: ProgressController, window: MainWindow
    ) -> None:
        window.start_requested.emit()
        window.stop_requested.emit()
        assert window._ui.startButton.isEnabled()

    def test_stop_disables_stop_button(
        self, controller: ProgressController, window: MainWindow
    ) -> None:
        window.start_requested.emit()
        window.stop_requested.emit()
        assert not window._ui.stopButton.isEnabled()


class TestCancelWorkflow:
    """F-09 and F-10: cancelling via the progress dialog."""

    def test_cancel_hides_dialog(
        self,
        controller: ProgressController,
        window: MainWindow,
        dialog: ProgressDialog,
    ) -> None:
        window.start_requested.emit()
        dialog.cancelled.emit()
        assert not dialog.isVisible()

    def test_cancel_enables_start_button(
        self,
        controller: ProgressController,
        window: MainWindow,
        dialog: ProgressDialog,
    ) -> None:
        window.start_requested.emit()
        dialog.cancelled.emit()
        assert window._ui.startButton.isEnabled()

    def test_cancel_disables_stop_button(
        self,
        controller: ProgressController,
        window: MainWindow,
        dialog: ProgressDialog,
    ) -> None:
        window.start_requested.emit()
        dialog.cancelled.emit()
        assert not window._ui.stopButton.isEnabled()


class TestCompletion:
    """F-05 and F-06: natural completion at 100%."""

    @staticmethod
    def _run_to_completion(controller: ProgressController) -> None:
        """Manually fire timer ticks until progress reaches 100%."""
        for _ in range(100):
            controller._on_timer_tick()

    def test_completion_emits_progress_completed(
        self,
        controller: ProgressController,
        window: MainWindow,
        dialog: ProgressDialog,
        qtbot: QtBot,
    ) -> None:
        window.start_requested.emit()
        with qtbot.waitSignal(controller.progress_completed, timeout=1_000):
            self._run_to_completion(controller)

    def test_completion_hides_dialog(
        self,
        controller: ProgressController,
        window: MainWindow,
        dialog: ProgressDialog,
        qtbot: QtBot,
    ) -> None:
        window.start_requested.emit()
        with qtbot.waitSignal(controller.progress_completed, timeout=1_000):
            self._run_to_completion(controller)
        assert not dialog.isVisible()

    def test_completion_enables_start_button(
        self,
        controller: ProgressController,
        window: MainWindow,
        dialog: ProgressDialog,
        qtbot: QtBot,
    ) -> None:
        window.start_requested.emit()
        with qtbot.waitSignal(controller.progress_completed, timeout=1_000):
            self._run_to_completion(controller)
        assert window._ui.startButton.isEnabled()
