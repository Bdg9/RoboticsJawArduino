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
MAX_POINTS = 200       # Max points to show per actuator

# ==== Data Storage ====
actuator_data = {i: [] for i in range(6)}
timestamps = []

# ==== Set up Serial ====
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Let the Teensy reset

# ==== Setup Plot ====
fig, ax = plt.subplots(figsize=(12, 6))
lines = [ax.plot([], [], label=f'Actuator {i}')[0] for i in range(6)]

ax.set_xlim(0, MAX_POINTS)
ax.set_ylim(-255, 255)  # Adjust based on your expected speed range
ax.set_xlabel("Sample")
ax.set_ylabel("Speed")
ax.set_title("Live Actuator Target Speeds")
ax.legend()
ax.grid(True)

# ==== Animation Update Function ====
def update(frame):
    while ser.in_waiting:
        line = ser.readline().decode(errors='ignore').strip()
        match = re.match(r"Actuator (\d) target speed: (-?\d+\.?\d*)", line)
        if match:
            i = int(match.group(1))
            speed = float(match.group(2))
            actuator_data[i].append(speed)
            if len(actuator_data[i]) > MAX_POINTS:
                actuator_data[i].pop(0)

    # Update each line
    for i, line in enumerate(lines):
        y = actuator_data[i]
        x = list(range(len(y)))
        line.set_data(x, y)

    return lines

ani = animation.FuncAnimation(fig, update, interval=100)
plt.tight_layout()
plt.show()
ser.close()
