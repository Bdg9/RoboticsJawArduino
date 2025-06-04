import sys
import serial
import serial.tools.list_ports
import threading
import os
import time
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QComboBox,
    QSlider, QLabel, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout,
    QDialog, QGridLayout, QTextEdit, QFormLayout, QSpinBox
)
from PyQt5.QtCore import Qt, QTimer, QEvent, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QTextCursor
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
        form_layout = QFormLayout()

        self.x_spin = QSpinBox()
        self.x_spin.setRange(-1000, 1000)
        self.x_spin.setValue(0)
        self.x_spin.valueChanged.connect(self.send_position)

        self.y_spin = QSpinBox()
        self.y_spin.setRange(-1000, 1000)
        self.y_spin.setValue(0)
        self.y_spin.valueChanged.connect(self.send_position)

        self.z_spin = QSpinBox()
        self.z_spin.setRange(325, 474)
        self.z_spin.setValue(325)
        self.z_spin.valueChanged.connect(self.send_position)

        form_layout.addRow("X (mm):", self.x_spin)
        form_layout.addRow("Y (mm):", self.y_spin)
        form_layout.addRow("Z (mm):", self.z_spin)

        layout.addLayout(form_layout)

        set_origin_button = QPushButton("Set Origin")
        set_origin_button.clicked.connect(self.set_origin)
        layout.addWidget(set_origin_button)

        self.setLayout(layout)
        # Make the calibration window bigger so that the title is visible.
        self.resize(250, 150)

    def send_position(self):
        x = self.x_spin.value()
        y = self.y_spin.value()
        z = self.z_spin.value()
        command = f"set position:{x},{y},{z}"
        self.send_command(command)

    def set_origin(self):
        x = self.x_spin.value()
        y = self.y_spin.value()
        z = self.z_spin.value()
        command = f"set origin:{x},{y},{z}"
        self.send_command(command)


class RobotGUI(QMainWindow):
    # Add a signal to handle serial data safely from threads.
    serialDataReceived = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("X-Jaw")

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

        self.speed_label = QLabel("TIme interval between waypoints:")
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(0, 5000)
        self.speed_spin.setValue(1000)
        self.speed_spin.setFixedSize(80, 25)
        self.speed_spin.setSuffix(" ms")


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
        speed_layout.addWidget(self.speed_spin)
        speed_layout.setAlignment(Qt.AlignLeft)

        main_layout.addLayout(control_layout)
        main_layout.addLayout(speed_layout)
        main_layout.addWidget(self.canvas_3d)
        main_layout.addWidget(self.error_console)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        ports = list(serial.tools.list_ports.comports())
        # Pass the emit function of the signal as callback.
        self.serial = SerialReader(ports[0].device, 115200, self.serialDataReceived.emit)
        self.serial.start()

        self.start_button.clicked.connect(self.send_start)
        self.stop_button.clicked.connect(self.send_stop)
        self.calibrate_button.clicked.connect(self.open_calibration_window)
        self.speed_spin.valueChanged.connect(self.send_speed)
        self.trajectory_dropdown.activated.connect(self.send_trajectory)
        # intercept “about to show” to trigger list request
        self.trajectory_dropdown.popupAboutToBeShown.connect(self.load_trajectory_files)

        self.data = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(100)

        self.pending_files = None  # <-- new attribute to store file list

        # Connect the new signal to the handle_serial_data slot.
        self.serialDataReceived.connect(self.handle_serial_data)

    def eventFilter(self, source, event):
        if source == self.trajectory_dropdown.view() and event.type() == QEvent.Show:
            self.load_trajectory_files()
        return super().eventFilter(source, event)

    def load_trajectory_files(self):
        self.pending_files = None
        self.serial.write("list_csv_files")
        # Let the serial thread fetch the file list.
        QTimer.singleShot(500, self.update_trajectory_files)

    def update_trajectory_files(self):
        self.trajectory_dropdown.clear()
        if self.pending_files:
            for filename in self.pending_files:
                self.trajectory_dropdown.addItem(filename)
        else:
            self.trajectory_dropdown.addItem("No files found")

    def send_start(self):
        self.serial.write("start")
        self.log("Sent: start")

    def send_stop(self):
        self.serial.write("stop")
        self.log("Sent: stop")

    def open_calibration_window(self):
        # Disable main window buttons
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)

        self.serial.write("calibrate")
        
        self.cal_window = CalibrationWindow(self.serial.write)
        self.cal_window.setModal(True)
        self.cal_window.exec()
        
        # Re-enable buttons once the calibration window is closed
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(True)
        self.calibrate_button.setEnabled(True)

        self.serial.write("stop") # Ensure the robot moves back to stop state after calibration

    def send_trajectory(self):
        filename = self.trajectory_dropdown.currentText()
        self.log(f"dropdown")
        self.serial.write(f"trajectory:{filename}")
        self.log(f"Sent: trajectory:{filename}")
    
    def send_speed(self):
        value = self.speed_spin.value()
        self.serial.write(f"set fixed interval:{value}")
        self.log(f"Sent: set fixed interval:{value}")

    # Remove any direct calls to update GUI from the serial thread.
    def handle_serial_data(self, line):
        # If this is the file list sent from the SD card, capture it and do not process further.
        if ".csv" in line:
            self.pending_files = [fn.strip() for fn in line.split(',') if fn.strip().endswith('.csv')]
            return
        try:
            values = list(map(float, line.split(',')))
            if len(values) >= 5:
                self.data.append(values)
        except ValueError:
            self.log(f"Non-numeric serial input: {line}")

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S] ")
        self.error_console.append(timestamp + message)
        self.error_console.moveCursor(QTextCursor.End)

    def update_plots(self):
        if not self.data:
            return

        # arr = np.array(self.data[-100:])
        # x, y, z, c1, c2 = arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3], arr[:, 4]

        # self.ax3d.clear()
        # self.ax3d.plot(x, y, z, color='blue')
        # self.ax3d.set_xlabel('X')
        # self.ax3d.set_ylabel('Y')
        # self.ax3d.set_zlabel('Z')

        # self.canvas_3d.draw()

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
