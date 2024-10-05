import os.path
import sys
import traceback

import pandas as pd
from PyQt6.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QComboBox, QProgressBar, QGridLayout,
                             QLineEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QFrame, QSizePolicy)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont

from config.configManager import ConfigManager
from config.log import SingletonLogger
from utils.DecryptScript import DecryptScript
from utils.ExtractScript import ExtractScript
from utils.MergeScript import MergeScript
import asyncio


class WorkerThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(bool, str)

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = asyncio.run(self.function(*self.args, **self.kwargs))
            self.finished.emit(True, "")
        except Exception as e:
            error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
            print(error_msg)
            self.finished.emit(False, error_msg)


class StatusLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedWidth(100)
        self.setStatus("Not Started")

    def setStatus(self, status):
        self.setText(status)
        if status == "Not Started":
            self.setStyleSheet("background-color: lightgray; color: black; border-radius: 5px;")
        elif status == "In Progress":
            self.setStyleSheet("background-color: yellow; color: black; border-radius: 5px;")
        elif status == "Completed":
            self.setStyleSheet("background-color: lightgreen; color: black; border-radius: 5px;")
        elif status == "Failed":
            self.setStyleSheet("background-color: red; color: white; border-radius: 5px;")

class OperationFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("""
            OperationFrame {
                border: 1px solid #CCCCCC;
                border-radius: 10px;
                background-color: #F5F5F5;
            }
        """)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.cfg_manager = ConfigManager()
        self.logger = SingletonLogger()
        self.decryptScriptObj = DecryptScript()
        self.extractScriptObj = ExtractScript()
        extract_script_folder = self.cfg_manager.get("output_folder_extract", "./data/3-merge")
        if os.path.exists(os.path.join(extract_script_folder, 'cfgSound.csv')) \
                and os.path.exists(os.path.join(extract_script_folder, 'cfgSound1.csv')):
            self.cfgSound_mergeScriptObj = MergeScript(
                pd.read_csv(os.path.join(extract_script_folder, 'cfgSound.csv'), dtype='str')
            )
            self.cfgSound1_mergeScriptObj = MergeScript(
                pd.read_csv(os.path.join(extract_script_folder, 'cfgSound1.csv'), dtype='str')
            )
        else:
            self.cfgSound_mergeScriptObj = None
            self.cfgSound1_mergeScriptObj = None

    def initUI(self):
        self.setWindowTitle('Decrypt-Extract-Merge-Pack-Encrypt')
        self.setGeometry(750, 200, 400, 600)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        app_font = QFont("Arial", 10)
        self.setFont(app_font)

        # Platform selection
        platform_layout = QHBoxLayout()
        platform_layout.addWidget(QLabel('Platform:'))
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(['Android', 'iOS'])
        platform_layout.addWidget(self.platform_combo)
        platform_layout.addStretch(1)
        main_layout.addLayout(platform_layout)

        # Operations
        operations = [
            ("1. Decrypt", self.decrypt),
            ("2. Extract", self.extract),
            ("3.1 Detach", self.detach),
            ("3.2 Merge", self.merge),
            ("4. Pack", self.pack),
            ("5. Encrypt", self.encrypt)
        ]

        self.status_labels = []
        for i, (title, func) in enumerate(operations):
            frame = OperationFrame()
            frame_layout = QVBoxLayout(frame)

            if title == "3.1 Detach":
                # Detach button and status
                detach_layout = QHBoxLayout()
                detach_button = QPushButton(title)
                detach_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                detach_button.clicked.connect(func)
                detach_layout.addWidget(detach_button, 4)
                detach_layout.addStretch(1)
                detach_status = StatusLabel()
                detach_status.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.status_labels.append(detach_status)
                detach_layout.addWidget(detach_status, 4)
                frame_layout.addLayout(detach_layout)

                # Model and Key inputs
                input_layout = QGridLayout()
                input_layout.addWidget(QLabel("Model:"), 0, 0)
                self.model_input = QLineEdit()
                self.model_input.setPlaceholderText('Enter model')
                input_layout.addWidget(self.model_input, 0, 1)
                input_layout.addWidget(QLabel("Key:"), 1, 0)
                self.key_input = QLineEdit()
                self.key_input.setPlaceholderText('Enter key')
                input_layout.addWidget(self.key_input, 1, 1)
                frame_layout.addLayout(input_layout)

                frame.setFixedHeight(120)  # Increased height for Detach operation
            elif title == "3.2 Merge":
                op_layout = QHBoxLayout()
                button = QPushButton(title)
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                button.clicked.connect(func)
                op_layout.addWidget(button, 4)
                op_layout.addStretch(1)
                status = StatusLabel()
                status.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.status_labels.append(status)
                op_layout.addWidget(status, 4)
                frame_layout.addLayout(op_layout)
                frame.setFixedHeight(60)
            else:
                op_layout = QHBoxLayout()
                button = QPushButton(title)
                button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                button.clicked.connect(func)
                op_layout.addWidget(button, 4)
                op_layout.addStretch(1)
                status = StatusLabel()
                status.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                self.status_labels.append(status)
                op_layout.addWidget(status, 4)
                frame_layout.addLayout(op_layout)
                frame.setFixedHeight(60)

            main_layout.addWidget(frame)

        # Progress bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        self.setLayout(main_layout)

        # Set styles
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                color: black;
            }
            QPushButton {
                background-color: #E0E0E0;
                border: none;
                padding: 8px;
                border-radius: 5px;
            }
            QLabel {
                background-color: #F5F5F5;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #D0D0D0;
            }
            QLineEdit, QComboBox {
                border: 1px solid #CCCCCC;
                padding: 5px;
                border-radius: 5px;
            }
            QProgressBar {
                border: 1px solid #CCCCCC;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 5px;
            }
        """)

    def run_task(self, index, task):
        self.status_labels[index].setStatus("In Progress")
        self.worker = WorkerThread(task)
        self.worker.finished.connect(lambda success, error_msg: self.onFinished(index, success, error_msg))
        self.worker.start()

    def onFinished(self, index, success, error_msg):
        self.progress_bar.setValue(100)
        status = "Completed" if success else "Failed"
        self.status_labels[index].setStatus(status)
        if not success:
            QMessageBox.critical(self, "Error", f"Operation failed:\n{error_msg}")
        print(f"Operation {status}")

    def decrypt(self):
        self.run_task(0, self.decryptScriptObj.decrypt)

    def extract(self):
        self.run_task(1, self.extractScriptObj.run_extraction)


    def detach(self):
        model = self.model_input.text()
        key = self.key_input.text()
        if not model or not key:
            QMessageBox.warning(self, "Input Error", "Please enter both model and key.")
            return
        self.run_task(2, MergeScript(None).mergeScript)

    def merge(self):
        model = self.model_input.text()
        key = self.key_input.text()
        if not model or not key:
            QMessageBox.warning(self, "Input Error", "Please enter both model and key.")
            return
        self.run_task(2, MergeScript(None).mergeScript)

    def pack(self):
        self.run_task(3, self.extractScriptObj.run_packaging)

    def encrypt(self):
        self.run_task(4, self.decryptScriptObj.encrypt)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())