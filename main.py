import sys
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog,
                             QLabel, QComboBox, QProgressBar, QGridLayout)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QColor
from DecryptScript import DecryptScript
from ExtractScript import ExtractScript
from MergeScript import MergeScript
import asyncio


class WorkerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool)  # True for success, False for failure

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            asyncio.run(self.function(*self.args, **self.kwargs))
            self.finished.emit(True)  # Success
        except Exception as e:
            print(f"Error: {e}")
            self.finished.emit(False)  # Failure


class StatusLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStatus("Not Started")

    def setStatus(self, status):
        self.setText(status)
        if status == "Not Started":
            self.setStyleSheet("background-color: lightgray; border: 1px solid black;")
        elif status == "In Progress":
            self.setStyleSheet("background-color: yellow; border: 1px solid black;")
        elif status == "Completed":
            self.setStyleSheet("background-color: lightgreen; border: 1px solid black;")
        elif status == "Failed":
            self.setStyleSheet("background-color: red; border: 1px solid black;")


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.decryptScriptObj = DecryptScript()
        self.extractScriptObj = ExtractScript()

    def initUI(self):
        self.setWindowTitle('Decrypt-Extract-Merge-Pack-Encrypt')
        self.setGeometry(100, 100, 600, 400)  # Increased width to accommodate status labels

        layout = QGridLayout()

        # Platform selection
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(['Android', 'iOS'])
        layout.addWidget(QLabel('Platform:'), 1, 0)
        layout.addWidget(self.platform_combo, 1, 1, 1, 2)

        # Action buttons and status labels
        self.buttons = []
        self.status_labels = []
        actions = ['Decrypt', 'Extract', 'Merge', 'Pack', 'Encrypt']
        for i, action in enumerate(actions):
            button = QPushButton(f'{i + 1}. {action}')
            button.clicked.connect(getattr(self, action.lower()))
            layout.addWidget(button, i + 2, 0, 1, 2)
            self.buttons.append(button)

            status_label = StatusLabel()
            layout.addWidget(status_label, i + 2, 2)
            self.status_labels.append(status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar, len(actions) + 2, 0, 1, 3)

        self.setLayout(layout)

    # def selectFile(self):
    #     file_name, _ = QFileDialog.getOpenFileName(self, "Select File")
    #     if file_name:
    #         self.file_label.setText(file_name)

    def decrypt(self):
        self.run_task(0, self.decryptScriptObj.decrypt)

    def extract(self):
        self.run_task(1, self.extractScriptObj.run_extraction)

    def merge(self):
        self.run_task(2, MergeScript(None).mergeScript)

    def pack(self):
        self.run_task(3, self.extractScriptObj.run_packaging)

    def encrypt(self):
        self.run_task(4, self.decryptScriptObj.encrypt)

    def run_task(self, index, task):
        self.status_labels[index].setStatus("In Progress")
        self.worker = WorkerThread(task)
        self.worker.finished.connect(lambda success: self.onFinished(index, success))
        self.worker.start()

    def onFinished(self, index, success):
        self.progress_bar.setValue(100)
        self.status_labels[index].setStatus("Completed" if success else "Failed")
        print(f"Operation {'completed' if success else 'failed'}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())