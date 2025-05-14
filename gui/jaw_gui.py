import sys
import serial
import serial.tools.list_ports
import threading
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QComboBox,
    QSlider, QLabel, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout,
    QDialog, QGridLayout, QTextEdit
)
from PyQt5.QtCore import Qt, QTimer, QEvent, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

class DynamicCombo(QComboBox):
    popupAboutToBeShown = pyqtSignal()          # <- custom signal

    # call order: Qt → showPopup() → (our emit) → super() → dropdown opens
    def showPopup(self):
        self.popupAboutToBeShown.emit()
        super().showPopup()

class SerialReader(threading.Thread):
    def __init__(self, port, baudrate, callback):
        super().__init__(daemon=True)
        self.serial = serial.Serial(port, baudrate, timeout=1)
        self.callback = callback
        self._running = True

    def run(self):
        while self._running:
            if self.serial.in_waiting:
                line = self.serial.readline().decode().strip()
                self.callback(line)

    def write(self, message):
        self.serial.write((message + "\n").encode())

    def stop(self):
        self._running = False
        self.serial.close()


class CalibrationWindow(QDialog):
    def __init__(self, send_command):
        super().__init__()
        self.setWindowTitle("Calibration")
        self.send_command = send_command
        self.setModal(True)

        layout = QVBoxLayout()
        grid = QGridLayout()

        self.set_origin_button = QPushButton("Set Origin")
        self.set_origin_button.clicked.connect(lambda: self.send_command("set_origin"))
        layout.addWidget(self.set_origin_button)

        self.up_button = QPushButton("↑")
        self.down_button = QPushButton("↓")
        self.left_button = QPushButton("←")
        self.right_button = QPushButton("→")

        self.up_button.clicked.connect(lambda: self.send_command("move_up"))
        self.down_button.clicked.connect(lambda: self.send_command("move_down"))
        self.left_button.clicked.connect(lambda: self.send_command("move_left"))
        self.right_button.clicked.connect(lambda: self.send_command("move_right"))

        grid.addWidget(self.up_button, 0, 1)
        grid.addWidget(self.left_button, 1, 0)
        grid.addWidget(self.right_button, 1, 2)
        grid.addWidget(self.down_button, 2, 1)

        layout.addLayout(grid)
        self.setLayout(layout)

    def keyPressEvent(self, event):
        key_map = {
            Qt.Key_Up: "move_up",
            Qt.Key_Down: "move_down",
            Qt.Key_Left: "move_left",
            Qt.Key_Right: "move_right"
        }
        if event.key() in key_map:
            self.send_command(key_map[event.key()])


class RobotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Robotic jaw")

        main_layout = QVBoxLayout()
        control_layout = QHBoxLayout()
        speed_layout = QHBoxLayout()

        self.start_button = QPushButton("Start")
        self.stop_button = QPushButton("Stop")
        self.calibrate_button = QPushButton("Calibrate")

        self.trajectory_label = QLabel("Trajectory:")
        self.trajectory_dropdown = DynamicCombo()
        self.trajectory_dropdown.addItem("‑‑ click to load from SD card ‑‑")
        self.trajectory_dropdown.view().window().setWindowFlags(                     
            self.trajectory_dropdown.view().window().windowFlags() | Qt.Popup)       

        self.speed_label = QLabel("Speed:")
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setMinimum(1)
        self.speed_slider.setMaximum(100)
        self.speed_slider.setValue(50)

        self.canvas_3d = FigureCanvas(Figure(figsize=(4, 3)))
        self.ax3d = self.canvas_3d.figure.add_subplot(111, projection='3d')

        self.error_console = QTextEdit()
        self.error_console.setReadOnly(True)
        self.error_console.setFixedHeight(100)
        self.error_console.setPlaceholderText("Console output / errors...")

        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.stop_button)
        control_layout.addWidget(self.trajectory_label)
        control_layout.addWidget(self.trajectory_dropdown)
        control_layout.addStretch()
        control_layout.addWidget(self.calibrate_button)

        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_slider)

        main_layout.addLayout(control_layout)
        main_layout.addLayout(speed_layout)
        main_layout.addWidget(self.canvas_3d)
        main_layout.addWidget(self.error_console)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        ports = list(serial.tools.list_ports.comports())
        self.serial = SerialReader(ports[0].device, 115200, self.handle_serial_data)
        self.serial.start()

        self.start_button.clicked.connect(self.send_start)
        self.stop_button.clicked.connect(self.send_stop)
        self.calibrate_button.clicked.connect(self.open_calibration_window)
        self.speed_slider.valueChanged.connect(self.send_speed)
        self.trajectory_dropdown.activated.connect(self.send_trajectory)
        # intercept “about to show” to trigger request_list()
        self.trajectory_dropdown.popupAboutToBeShown.connect(self.load_trajectory_files)

        self.data = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(100)

    def eventFilter(self, source, event):
        if source == self.trajectory_dropdown.view() and event.type() == QEvent.Show:
            self.load_trajectory_files()
        return super().eventFilter(source, event)

    def load_trajectory_files(self):
        self.serial.write("list_csv_files")
        self.trajectory_dropdown.clear()
        # receive the file names from the serial port, they are sent in one line with each name separated by a comma
        line = self.serial.serial.readline().decode().strip()
        if line:
            filenames = line.split(',')
            for filename in filenames:
                if filename.endswith('.csv'):
                    self.trajectory_dropdown.addItem(filename)

    def send_start(self):
        self.serial.write("start")
        self.log("Sent: start")

    def send_stop(self):
        self.serial.write("stop")
        self.log("Sent: stop")

    def open_calibration_window(self):
        self.cal_window = CalibrationWindow(self.serial.write)
        self.cal_window.exec()

    def send_speed(self):
        value = self.speed_slider.value()
        self.serial.write(f"speed:{value}")
        self.log(f"Sent: speed:{value}")

    def send_trajectory(self):
        filename = self.trajectory_dropdown.currentText()
        self.log(f"dropdown")
        self.serial.write(f"trajectory:{filename}")
        self.log(f"Sent: trajectory:{filename}")

    def handle_serial_data(self, line):
        try:
            values = list(map(float, line.split(',')))
            if len(values) >= 5:
                self.data.append(values)
        except ValueError:
            self.log(f"Non-numeric serial input: {line}")

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.error_console.append(timestamp + message)

    def update_plots(self):
        if not self.data:
            return

        arr = np.array(self.data[-100:])
        x, y, z, c1, c2 = arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3], arr[:, 4]

        self.ax3d.clear()
        self.ax3d.plot(x, y, z, color='blue')
        self.ax3d.set_xlabel('X')
        self.ax3d.set_ylabel('Y')
        self.ax3d.set_zlabel('Z')

        self.ax1d.clear()
        self.ax1d.plot(c1, label='Curve 1')
        self.ax1d.plot(c2, label='Curve 2')
        self.ax1d.legend()
        self.ax1d.set_xlabel('Time')

        self.canvas_3d.draw()
        self.canvas_1d.draw()

    def closeEvent(self, event):
        self.serial.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RobotGUI()
    window.setWindowIcon(QIcon("app_icon.ico"))
    window.resize(900, 800)
    window.show()
    sys.exit(app.exec())
