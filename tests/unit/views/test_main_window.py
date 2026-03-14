"""Tests for the MainWindow view.

Tests follow pyqt_guidelines.md §6 — test behavior, not layout.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from pytestqt.qtbot import QtBot

from simple.views.main_window import MainWindow


@pytest.fixture()
def window(qtbot: QtBot) -> MainWindow:
    """Return a MainWindow registered for automatic cleanup."""
    w = MainWindow()
    qtbot.addWidget(w)
    return w


class TestInitialState:
    """F-04, F-06, F-08, F-10 (idle state): Start enabled, Stop disabled."""

    def test_start_button_initially_enabled(self, window: MainWindow) -> None:
        assert window._ui.startButton.isEnabled()

    def test_stop_button_initially_disabled(self, window: MainWindow) -> None:
        assert not window._ui.stopButton.isEnabled()


class TestSetRunning:
    """set_running() toggles button states correctly."""

    def test_set_running_true_disables_start(self, window: MainWindow) -> None:
        window.set_running(True)
        assert not window._ui.startButton.isEnabled()

    def test_set_running_true_enables_stop(self, window: MainWindow) -> None:
        window.set_running(True)
        assert window._ui.stopButton.isEnabled()

    def test_set_running_false_enables_start(self, window: MainWindow) -> None:
        window.set_running(True)
        window.set_running(False)
        assert window._ui.startButton.isEnabled()

    def test_set_running_false_disables_stop(self, window: MainWindow) -> None:
        window.set_running(True)
        window.set_running(False)
        assert not window._ui.stopButton.isEnabled()


class TestSignals:
    """Buttons emit the correct signals (F-01, F-07)."""

    def test_start_button_emits_start_requested(
        self, window: MainWindow, qtbot: QtBot
    ) -> None:
        window.show()
        with qtbot.waitSignal(window.start_requested, timeout=1000):
            qtbot.mouseClick(window._ui.startButton, Qt.MouseButton.LeftButton)

    def test_stop_button_emits_stop_requested(
        self, window: MainWindow, qtbot: QtBot
    ) -> None:
        window.set_running(True)
        window.show()
        with qtbot.waitSignal(window.stop_requested, timeout=1000):
            qtbot.mouseClick(window._ui.stopButton, Qt.MouseButton.LeftButton)


class TestMenuBar:
    """Menu bar items are present with correct shortcuts (§3.5)."""

    def test_menubar_has_file_menu(self, window: MainWindow) -> None:
        assert window._ui.menuFile is not None

    def test_menubar_has_edit_menu(self, window: MainWindow) -> None:
        assert window._ui.menuEdit is not None

    def test_menubar_has_help_menu(self, window: MainWindow) -> None:
        assert window._ui.menuHelp is not None

    def test_action_new_shortcut(self, window: MainWindow) -> None:
        assert window._ui.actionNew.shortcut().toString() == "Ctrl+N"

    def test_action_open_shortcut(self, window: MainWindow) -> None:
        assert window._ui.actionOpen.shortcut().toString() == "Ctrl+O"

    def test_action_save_shortcut(self, window: MainWindow) -> None:
        assert window._ui.actionSave.shortcut().toString() == "Ctrl+S"

    def test_action_exit_shortcut(self, window: MainWindow) -> None:
        assert window._ui.actionExit.shortcut().toString() == "Ctrl+Q"

    def test_action_undo_shortcut(self, window: MainWindow) -> None:
        assert window._ui.actionUndo.shortcut().toString() == "Ctrl+Z"

    def test_action_redo_shortcut(self, window: MainWindow) -> None:
        assert window._ui.actionRedo.shortcut().toString() == "Ctrl+Y"

    def test_action_cut_shortcut(self, window: MainWindow) -> None:
        assert window._ui.actionCut.shortcut().toString() == "Ctrl+X"

    def test_action_copy_shortcut(self, window: MainWindow) -> None:
        assert window._ui.actionCopy.shortcut().toString() == "Ctrl+C"

    def test_action_paste_shortcut(self, window: MainWindow) -> None:
        assert window._ui.actionPaste.shortcut().toString() == "Ctrl+V"

    def test_all_menu_actions_have_icons(self, window: MainWindow) -> None:
        actions = [
            window._ui.actionNew,
            window._ui.actionOpen,
            window._ui.actionSave,
            window._ui.actionExit,
            window._ui.actionUndo,
            window._ui.actionRedo,
            window._ui.actionCut,
            window._ui.actionCopy,
            window._ui.actionPaste,
            window._ui.actionAbout,
        ]
        for action in actions:
            assert not action.icon().isNull(), f"{action.text()} has no icon"
