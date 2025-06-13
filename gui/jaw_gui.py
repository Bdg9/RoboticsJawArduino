import sys
import serial
import serial.tools.list_ports
import threading
import os
import time
import re                  # <-- new import for regex
import matplotlib.pyplot as plt   # <-- new import for plotting
import csv  # <-- add this at the top if not already present
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

ROOT_DIR = "..\Results"  # Directory to save results

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
        
        # New attributes to store parsed serial messages 
        self.actuator_data = []   # each entry will be a dict with actuator values
        self.pose_data = []       # each entry will be a dict with pose values
        self.force_data_front = []  # each entry will be a dict with force values for front load cell
        self.force_data_backr = []   # each entry will be a dict with force values for back right load cell
        self.force_data_backl = []   # each entry will be a dict with force values for back left load cell
        self.force_data_total = []  # each entry will be a dict with total force values
        self.debug_actuator_data = []  # each entry will be a dict with debug actuator values
        main_layout = QVBoxLayout()
        
        grid_layout = QGridLayout()
        grid_layout.setHorizontalSpacing(20)
        grid_layout.setVerticalSpacing(10)

        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(100, 50)
        self.stop_button = QPushButton("Stop")
        self.stop_button.setFixedSize(100, 50)
        self.calibrate_button = QPushButton("Calibrate")

        self.trajectory_label = QLabel("Trajectory:")
        self.trajectory_dropdown = DynamicCombo()
        self.trajectory_dropdown.addItem("‑‑ click to load from SD card ‑‑")
        self.trajectory_dropdown.view().window().setWindowFlags(                     
            self.trajectory_dropdown.view().window().windowFlags() | Qt.Popup)       

        self.speed_label = QLabel("TIme interval between waypoints:")
        self.speed_spin = QSpinBox()
        self.speed_spin.setRange(0, 5000)
        self.speed_spin.setValue(100)
        self.speed_spin.setFixedSize(80, 25)
        self.speed_spin.setSuffix(" ms")

        self.canvas_3d = FigureCanvas(Figure(figsize=(4, 3)))
        self.ax3d = self.canvas_3d.figure.add_subplot(111, projection='3d')

        self.error_console = QTextEdit()
        self.error_console.setReadOnly(True)
        self.error_console.setFixedHeight(100)
        self.error_console.setPlaceholderText("Console output / errors...")

        # Left column: put start and stop vertically.
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        grid_layout.addLayout(button_layout, 0, 0, 2, 1)   # spans two rows in the first column

        # Right first row: trajectory label, dropdown, stretch, and calibrate button.
        traj_layout = QHBoxLayout()
        traj_layout.addWidget(self.trajectory_label)
        traj_layout.addWidget(self.trajectory_dropdown)
        traj_layout.addStretch()
        traj_layout.addWidget(self.calibrate_button)
        grid_layout.addLayout(traj_layout, 0, 1)            # first row, second column

        # Right second row: only the speed spin (aligned to left).
        speed_layout = QHBoxLayout()
        speed_layout.addWidget(self.speed_label)
        speed_layout.addWidget(self.speed_spin)
        speed_layout.addStretch()  # Add stretch to push the spin box to the left
        grid_layout.addLayout(speed_layout, 1, 1)          # second row, second column

        main_layout.addLayout(grid_layout)
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
        # When stop is pressed, generate the plots from the saved serial messages.
        self.generate_plots()
        self.generateForcePlots()

    def open_calibration_window(self):
        # Disable main window buttons
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)

        self.serial.write("calibrate")
        
        self.cal_window = CalibrationWindow(self.serial.write)
        self.cal_window.setModal(True)
        self.cal_window.exec()

        # Plot force data after calibration
        #self.generateForcePlots()
        #self.generateDebugActuatorPlots()
        
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

    # Updated serial handling to capture actuator and pose messages.
    def handle_serial_data(self, line):
        # If this is the file list sent from the SD card, capture it and do not process further.
        if ".csv" in line:
            self.pending_files = [fn.strip() for fn in line.split(',') if fn.strip().endswith('.csv')]
            return
        
        # Check if line belongs to an actuator message.
        if line.startswith("Actuator "):
            actuator_pattern = r"Actuator (\d+)\s+target speed:\s*([^,]+),\s*target length:\s*([^,]+),\s*current length:\s*([^,]+),\s*time:\s*(\d+)"
            match = re.match(actuator_pattern, line)
            if match:
                data = {
                    "actuator": int(match.group(1)),
                    "speed": float(match.group(2)),
                    "target_length": float(match.group(3)),
                    "current_length": float(match.group(4)),
                    "time": int(match.group(5))
                }
                self.actuator_data.append(data)
            return

        # Check if line belongs to a pose message.
        if line.startswith("Pose:"):
            pose_pattern = r"Pose:\s*x:\s*([^,]+),\s*y:\s*([^,]+),\s*z:\s*([^,]+),\s*roll:\s*([^,]+),\s*pitch:\s*([^,]+),\s*yaw:\s*([^,]+),\s*time:\s*(\d+)"
            match = re.match(pose_pattern, line)
            if match:
                data = {
                    "x": float(match.group(1)),
                    "y": float(match.group(2)),
                    "z": float(match.group(3)),
                    "roll": float(match.group(4)),
                    "pitch": float(match.group(5)),
                    "yaw": float(match.group(6)),
                    "time": int(match.group(7))
                }
                self.pose_data.append(data)
            return

        # Check if line belongs to a force message.
        if line.startswith("Total Force - X:"):
            force_pattern = r"Total Force - X:\s*([^,]+),\s*Y:\s*([^,]+),\s*Z:\s*([^,]+),\s*Time:\s*(\d+)"
            match = re.match(force_pattern, line)
            if match:
                data = {
                    "Fx": float(match.group(1)),
                    "Fy": float(match.group(2)),
                    "Fz": float(match.group(3)),
                    "time": int(match.group(4))
                }
                self.force_data_total.append(data)
            return

        if line.startswith("Front Force - X:"):
            force_pattern = r"Front Force - X:\s*([^,]+),\s*Y:\s*([^,]+),\s*Z:\s*([^,]+),\s*Time:\s*(\d+)"
            match = re.match(force_pattern, line)
            if match:
                data = {
                    "Fx": float(match.group(1)),
                    "Fy": float(match.group(2)),
                    "Fz": float(match.group(3)),
                    "time": int(match.group(4))
                }
                self.force_data_front.append(data)
            return
        if line.startswith("Back Right Force - X:"):
            force_pattern = r"Back Right Force - X:\s*([^,]+),\s*Y:\s*([^,]+),\s*Z:\s*([^,]+),\s*Time:\s*(\d+)"
            match = re.match(force_pattern, line)
            if match:
                data = {
                    "Fx": float(match.group(1)),
                    "Fy": float(match.group(2)),
                    "Fz": float(match.group(3)),
                    "time": int(match.group(4))
                }
                self.force_data_backr.append(data)
            return
        if line.startswith("Back Left Force - X:"):
            force_pattern = r"Back Left Force - X:\s*([^,]+),\s*Y:\s*([^,]+),\s*Z:\s*([^,]+),\s*Time:\s*(\d+)"
            match = re.match(force_pattern, line)
            if match:
                data = {
                    "Fx": float(match.group(1)),
                    "Fy": float(match.group(2)),
                    "Fz": float(match.group(3)),
                    "time": int(match.group(4))
                }
                self.force_data_backl.append(data)
            return

        if line.startswith("Debug Actuator"):         
            debug_actuator_pattern = r"Debug Actuator\s*(\d+)\s*raw pot value:\s*([\d.]+),\s*length:\s*([\d.]+),\s*filtered length:\s*([\d.]+),?\s*time:\s*(\d+)" 
            match = re.match(debug_actuator_pattern, line)
            if match:
                data = {
                    "actuator": int(match.group(1)),
                    "raw_value": float(match.group(2)),
                    "length": float(match.group(3)),
                    "filtered_length": float(match.group(4)),
                    "time": int(match.group(5))
                }
                # Append to actuator_data for consistency, or handle separately if needed.
                self.debug_actuator_data.append(data)
        # Fallback: try to process as generic numeric data.
        try:
            values = list(map(float, line.split(',')))
            if len(values) >= 5:
                self.data.append(values)
        except ValueError:
            self.log(line) 

    def log(self, message):
        timestamp = time.strftime("[%H:%M:%S] ")
        full_message = timestamp + message
        # Wrap each message in its own paragraph so that the styling is isolated.
        if message.startswith("Warning"):
            colored_message = f'<p style="color: orange; margin: 0;">{full_message}</p>'
        elif message.startswith("Error"):
            colored_message = f'<p style="color: red; margin: 0;">{full_message}</p>'
        else:
            colored_message = f'<p style="margin: 0;">{full_message}</p>'
        self.error_console.append(colored_message)
        self.error_console.moveCursor(QTextCursor.End)

    def update_plots(self):
        if not self.data:
            return

        # ...existing code for 3D plot (if needed)...
        # arr = np.array(self.data[-100:])
        # x, y, z, c1, c2 = arr[:, 0], arr[:, 1], arr[:, 2], arr[:, 3], arr[:, 4]

        # self.ax3d.clear()
        # self.ax3d.plot(x, y, z, color='blue')
        # self.ax3d.set_xlabel('X')
        # self.ax3d.set_ylabel('Y')
        # self.ax3d.set_zlabel('Z')

        # self.canvas_3d.draw()

    def generate_plots(self):
        # Ensure there is data to plot.
        if not self.actuator_data and not self.pose_data:
            self.log("No actuator or pose data captured for plotting.")
            return

        # Get a base filename from the selected trajectory file.
        base_filename = self.trajectory_dropdown.currentText().strip()
        base_filename = base_filename.replace(" ", "_")
        filename = base_filename.replace(".csv", "")
        speed = self.speed_spin.value()
        timestamp = time.strftime("%Y%m%d-%H%M%S")

        # --- Plot 1: For 6 actuators: target length and current length ---
        fig1, axs1 = plt.subplots(3, 2, figsize=(10, 8))
        axs1 = axs1.flatten()
        for i in range(6):
            act_data = [d for d in self.actuator_data if d["actuator"] == i]
            if act_data:
                #change time so that the first point is at 0 and it's in seconds and not ms
                times = [d["time"] for d in act_data]
                times = [(t - times[0]) / 1000 for t in times]  # Convert ms to seconds
                target_lengths = [d["target_length"] for d in act_data]
                current_lengths = [d["current_length"] for d in act_data]
                axs1[i].plot(times, target_lengths, label="Target Length")
                axs1[i].plot(times, current_lengths, label="Current Length")
                axs1[i].set_title(f"Actuator {i}")
                axs1[i].set_xlabel("Time (s)")
                axs1[i].set_ylabel("Length (mm)")
                axs1[i].legend()
            else:
                axs1[i].text(0.5, 0.5, "No Data", ha="center")
                axs1[i].set_title(f"Actuator {i}")
        fig1.tight_layout()
        lengths_filename = f"{ROOT_DIR}\\{filename}_{speed}_ms_lengths_{timestamp}.png"
        fig1.savefig(lengths_filename)
        self.log(f"Saved lengths plot: {lengths_filename}")

        # --- Plot 2: For 6 actuators: speed command ---
        fig2, axs2 = plt.subplots(3, 2, figsize=(10, 8))
        axs2 = axs2.flatten()
        for i in range(6):
            act_data = [d for d in self.actuator_data if d["actuator"] == i]
            if act_data:
                times = [d["time"] for d in act_data]
                times = [(t - times[0]) / 1000 for t in times]  # Convert ms to seconds
                speeds = [d["speed"] for d in act_data]
                axs2[i].plot(times, speeds, label="Speed", color="green")
                axs2[i].set_title(f"Actuator {i}")
                axs2[i].set_xlabel("Time (s)")
                axs2[i].set_ylabel("Speed")
                axs2[i].legend()
            else:
                axs2[i].text(0.5, 0.5, "No Data", ha="center")
                axs2[i].set_title(f"Actuator {i}")
        fig2.tight_layout()
        speeds_filename = f"{ROOT_DIR}\\{filename}_{speed}_ms_speeds_{timestamp}.png"
        fig2.savefig(speeds_filename)
        self.log(f"Saved speeds plot: {speeds_filename}")

        # --- Plot 3: For pose dimensions: x, y, z, roll, pitch, yaw ---
        dims = ["x", "y", "z", "roll", "pitch", "yaw"]
        unit = ["mm", "mm", "mm", "rad", "rad", "rad"]
        fig3, axs3 = plt.subplots(3, 2, figsize=(10, 8))
        axs3 = axs3.flatten()
        for idx, dim in enumerate(dims):
            if self.pose_data:
                times = [d["time"] for d in self.pose_data]
                times = [(t - times[0]) / 1000 for t in times]  # Convert ms to seconds
                values = [d[dim] for d in self.pose_data]
                axs3[idx].plot(times, values, label=dim, color="red")
                axs3[idx].set_title(dim)
                axs3[idx].set_xlabel("Time (s)")
                axs3[idx].set_ylabel(dim + f" ({unit[idx]})")
                axs3[idx].legend()
            else:
                axs3[idx].text(0.5, 0.5, "No Data", ha="center")
                axs3[idx].set_title(dim)
        fig3.tight_layout()
        pose_filename = f"{ROOT_DIR}\\{filename}_{speed}_ms_pose_{timestamp}.png"
        fig3.savefig(pose_filename)
        self.log(f"Saved pose plot: {pose_filename}")

        # --- Save actuator data to CSV ---
        actuator_csv_filename = f"{ROOT_DIR}\\{filename}_{speed}_ms_actuator_data_{timestamp}.csv"
        with open(actuator_csv_filename, mode='w', newline='') as csvfile:
            fieldnames = ["actuator", "speed", "target_length", "current_length", "time"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.actuator_data)
        self.log(f"Saved actuator data CSV: {actuator_csv_filename}")

        # --- Save pose data to CSV ---
        pose_csv_filename = f"{ROOT_DIR}\\{filename}_{speed}_ms_pose_data_{timestamp}.csv"
        with open(pose_csv_filename, mode='w', newline='') as csvfile:
            fieldnames = ["x", "y", "z", "roll", "pitch", "yaw", "time"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.pose_data)
        self.log(f"Saved pose data CSV: {pose_csv_filename}")

        # --- Close figures to free memory ---
        plt.close(fig1)
        plt.close(fig2)
        plt.close(fig3)

        # --- Clear data lists once plots are generated to free memory. ---
        self.actuator_data.clear()
        self.pose_data.clear()
    
    def generateForcePlots(self):
        # Ensure there is data to plot.
        if not self.force_data_front and not self.force_data_backr and not self.force_data_backl and not self.force_data_total:
            self.log("No force data captured for plotting.")
            return

        # Get a base filename from the selected trajectory file.
        base_filename = self.trajectory_dropdown.currentText().strip()
        base_filename = base_filename.replace(" ", "_")
        filename = base_filename.replace(".csv", "")
        speed = self.speed_spin.value()
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        dims = ["Fx", "Fy", "Fz"]
        load_cell_names = ["Front", "Back Right", "Back Left", "Total"]
        force_data = [self.force_data_front, self.force_data_backr, self.force_data_backl, self.force_data_total]

        # --- Plot: Force data for front, back right, back left, and total ---
        # One plot for each load cell.
        for i, load_cell_data in enumerate(force_data):
            if not load_cell_data:
                self.log(f"No data for {load_cell_names[i]} load cell.")
                continue
            
            fig, axs = plt.subplots(3, 1, figsize=(10, 8))
            axs = axs.flatten()
            for idx, dim in enumerate(dims):
                times = [d["time"] for d in load_cell_data]
                times = [(t - times[0]) / 1000 for t in times]
                values = [d[dim] for d in load_cell_data]
                axs[idx].plot(times, values, label=dim, color="blue")
                axs[idx].set_title(f"{load_cell_names[i]} Load Cell - {dim}")
                axs[idx].set_xlabel("Time (s)")
                axs[idx].set_ylabel(f"{dim} (N)")
                axs[idx].legend()
            fig.tight_layout()
            force_filename = f"{ROOT_DIR}\\{filename}_{speed}_ms_{load_cell_names[i].lower()}_force_{timestamp}.png"
            fig.savefig(force_filename)
            self.log(f"Saved {load_cell_names[i]} force plot: {force_filename}")
        # --- Log max z force on each load cell ---
        #only log max after the first 30 seconds of data collection
        stable_force_data_front = [d for d in self.force_data_front if d["time"] >= 30000]
        stable_force_data_backr = [d for d in self.force_data_backr if d["time"] >= 30000]
        stable_force_data_backl = [d for d in self.force_data_backl if d["time"] >= 30000]
        stable_force_data_total = [d for d in self.force_data_total if d["time"] >= 30000]
        max_forces = {
            "Front": max([d["Fz"] for d in stable_force_data_front], default=0),
            "Back Right": max([d["Fz"] for d in stable_force_data_backr], default=0),
            "Back Left": max([d["Fz"] for d in stable_force_data_backl], default=0),
            "Total": max([d["Fz"] for d in stable_force_data_total], default=0)
        }
        for load_cell, max_force in max_forces.items():
            self.log(f"Max Z Force on {load_cell} Load Cell: {max_force:.2f} N")
        # --- Save force data to CSV ---
        force_csv_filename = f"{ROOT_DIR}\\{filename}_{speed}_ms_force_data_{timestamp}.csv"
        with open(force_csv_filename, mode='w', newline='') as csvfile:
            fieldnames = ["Fx", "Fy", "Fz", "time"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data in self.force_data_front + self.force_data_backr + self.force_data_backl + self.force_data_total:
                writer.writerow(data)
        self.log(f"Saved force data CSV: {force_csv_filename}")

        # --- Close figures to free memory ---
        plt.close('all')

        # --- Clear data lists once plots are generated to free memory. ---
        self.force_data_backl.clear()
        self.force_data_backr.clear()
        self.force_data_front.clear()
        self.force_data_total.clear()
    
    def generateDebugActuatorPlots(self):
        # Ensure there is data to plot.
        if not self.debug_actuator_data:
            self.log("No debug actuator data captured for plotting.")
            return

        base_filename = self.trajectory_dropdown.currentText().strip()
        base_filename = base_filename.replace(" ", "_")
        filename = base_filename.replace(".csv", "")
        speed = self.speed_spin.value()
        timestamp = time.strftime("%Y%m%d-%H%M%S")

        # --- Figure 1: Plot for actuator length and filtered length ---
        fig1, axs1 = plt.subplots(3, 2, figsize=(10, 8))
        axs1 = axs1.flatten()
        for i in range(6):
            act_data = [d for d in self.debug_actuator_data if d["actuator"] == i]
            if act_data:
                times = [d["time"] for d in act_data]
                times = [(t - times[0]) / 1000 for t in times]  # convert ms to s
                lengths = [d["length"] for d in act_data]
                filtered_lengths = [d["filtered_length"] for d in act_data]
                axs1[i].plot(times, lengths, label="Length", color="green")
                axs1[i].plot(times, filtered_lengths, label="Filtered Length", color="red")
                axs1[i].set_title(f"Actuator {i}")
                axs1[i].set_xlabel("Time (s)")
                axs1[i].set_ylabel("Length (mm)")
                axs1[i].legend()
            else:
                axs1[i].text(0.5, 0.5, "No Data", ha="center")
                axs1[i].set_title(f"Actuator {i}")
        fig1.tight_layout()
        debug_length_filename = f"{ROOT_DIR}\\{filename}_{speed}_ms_debug_length_{timestamp}.png"
        fig1.savefig(debug_length_filename)
        self.log(f"Saved debug actuator length plot: {debug_length_filename}")

        # --- Figure 2: Plot for actuator raw potentiometer value ---
        fig2, axs2 = plt.subplots(3, 2, figsize=(10, 8))
        axs2 = axs2.flatten()
        for i in range(6):
            act_data = [d for d in self.debug_actuator_data if d["actuator"] == i]
            if act_data:
                times = [d["time"] for d in act_data]
                times = [(t - times[0]) / 1000 for t in times]  # convert ms to s
                raw_values = [d["raw_value"] for d in act_data]
                axs2[i].plot(times, raw_values, label="Raw Value", color="orange")
                axs2[i].set_title(f"Actuator {i}")
                axs2[i].set_xlabel("Time (s)")
                axs2[i].set_ylabel("Raw Value")
                axs2[i].legend()
            else:
                axs2[i].text(0.5, 0.5, "No Data", ha="center")
                axs2[i].set_title(f"Actuator {i}")
        fig2.tight_layout()
        debug_raw_filename = f"{ROOT_DIR}\\{filename}_{speed}_ms_debug_raw_{timestamp}.png"
        fig2.savefig(debug_raw_filename)
        self.log(f"Saved debug actuator raw value plot: {debug_raw_filename}")

        # --- Close figures to free memory ---
        plt.close(fig1)
        plt.close(fig2)
        # --- Clear data lists once plots are generated to free memory. ---
        self.debug_actuator_data.clear()

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
