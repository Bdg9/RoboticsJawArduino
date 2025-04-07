# pip install pyserial matplotlib 

import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import re
import time
import serial.tools.list_ports

def find_teensy_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Teensy" in port.description:
            return port.device  # e.g. 'COM4' or '/dev/ttyACM0'
    return None

def find_teensy_by_vid_pid():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if port.vid == 0x16C0 and port.pid in [0x0483, 0x0478]:
            return port.device
    return None

# ==== Configuration ====
SERIAL_PORT = find_teensy_port() or find_teensy_by_vid_pid()
if not SERIAL_PORT:
    raise RuntimeError("Teensy not found. Please plug it in.")
BAUD_RATE = 9600
MAX_POINTS = 500       # Max points to show per actuator

# ==== Data Storage ====
actuator_data = {i: [] for i in range(6)}
timestamps = []

# ==== Set up Serial ====
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Let the Teensy reset

# ==== Setup Plot for Speeds ====
fig, axes = plt.subplots(3, 2, figsize=(12, 8))  # Create a 3x2 grid of subplots
axes = axes.flatten()  # Flatten the 2D array of axes for easier indexing
speed_lines = []

for i, ax in enumerate(axes):
    line, = ax.plot([], [], label=f'Actuator {i} Speed')
    speed_lines.append(line)
    ax.set_xlim(0, MAX_POINTS)
    ax.set_ylim(-255, 255)  # Adjust based on your expected speed range
    ax.set_xlabel("Sample")
    ax.set_ylabel("Speed")
    ax.set_title(f"Actuator {i} Target Speeds")
    ax.legend()
    ax.grid(True)

# ==== Setup Plot for Lengths ====
fig2, axes2 = plt.subplots(3, 2, figsize=(12, 8))  # Create another 3x2 grid of subplots
axes2 = axes2.flatten()  # Flatten the 2D array of axes for easier indexing
length_lines = []

for i, ax in enumerate(axes2):
    target_line, = ax.plot([], [], label=f'Actuator {i} Target Length', color='blue')
    current_line, = ax.plot([], [], label=f'Actuator {i} Current Length', color='orange')
    length_lines.append((target_line, current_line))
    ax.set_xlim(0, MAX_POINTS)
    ax.set_ylim(350, 480)  # Adjust based on your expected length range
    ax.set_xlabel("Sample")
    ax.set_ylabel("Length")
    ax.set_title(f"Actuator {i} Lengths")
    ax.legend()
    ax.grid(True)

# ==== Animation Update Function ====
def update(frame):
    while ser.in_waiting:
        line = ser.readline().decode(errors='ignore').strip()
        match = re.match(r"Actuator (\d) target speed: (-?\d+\.?\d*), target length: (-?\d+\.?\d*), current length: (-?\d+\.?\d*)", line)
        if match:
            i = int(match.group(1))
            speed = float(match.group(2))
            target_length = float(match.group(3))
            current_length = float(match.group(4))

            # Update speed data
            actuator_data[i].append(speed)
            if len(actuator_data[i]) > MAX_POINTS:
                actuator_data[i].pop(0)

            # Update length data
            target_lengths[i].append(target_length)
            current_lengths[i].append(current_length)
            if len(target_lengths[i]) > MAX_POINTS:
                target_lengths[i].pop(0)
            if len(current_lengths[i]) > MAX_POINTS:
                current_lengths[i].pop(0)

    # Update speed lines
    for i, line in enumerate(speed_lines):
        y = actuator_data[i]
        x = list(range(len(y)))
        line.set_data(x, y)

    # Update length lines
    for i, (target_line, current_line) in enumerate(length_lines):
        x_target = list(range(len(target_lengths[i])))
        x_current = list(range(len(current_lengths[i])))
        target_line.set_data(x_target, target_lengths[i])
        current_line.set_data(x_current, current_lengths[i])

    return speed_lines + [line for pair in length_lines for line in pair]

# ==== Data Storage for Lengths ====
target_lengths = {i: [] for i in range(6)}
current_lengths = {i: [] for i in range(6)}

ani = animation.FuncAnimation(fig, update, interval=100)
ani2 = animation.FuncAnimation(fig2, update, interval=100)
plt.tight_layout()
plt.show()
ser.close()
