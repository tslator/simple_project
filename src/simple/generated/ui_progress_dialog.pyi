"""Type stub for generated ui_progress_dialog module."""

from PySide6.QtWidgets import QDialog, QProgressBar, QPushButton

class Ui_ProgressDialog:
    progressBar: QProgressBar
    cancelButton: QPushButton

    def setupUi(self, ProgressDialog: QDialog) -> None: ...
    def retranslateUi(self, ProgressDialog: QDialog) -> None: ...
