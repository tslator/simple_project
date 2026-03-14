"""Type stub for generated ui_main_window module."""

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QStatusBar,
    QWidget,
)

class Ui_MainWindow:
    centralwidget: QWidget
    greetingLabel: QLabel
    startButton: QPushButton
    stopButton: QPushButton
    menubar: QMenuBar
    menuFile: QMenu
    menuEdit: QMenu
    menuHelp: QMenu
    statusbar: QStatusBar
    actionNew: QAction
    actionOpen: QAction
    actionSave: QAction
    actionExit: QAction
    actionUndo: QAction
    actionRedo: QAction
    actionCut: QAction
    actionCopy: QAction
    actionPaste: QAction
    actionAbout: QAction

    def setupUi(self, MainWindow: QMainWindow) -> None: ...
    def retranslateUi(self, MainWindow: QMainWindow) -> None: ...
