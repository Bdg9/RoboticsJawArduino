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
speed_data = {i: [] for i in range(6)}
target_lengths = {i: [] for i in range(6)}
current_lengths = {i: [] for i in range(6)}

all_speed_data = []
all_target_lengths = []
all_current_lengths = []
timestamps = []

# ==== Set up Serial ====
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
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
    for _ in range(500):  # Process up to 500 lines per frame
        if ser.in_waiting:
            line = ser.readline().decode(errors='ignore').strip()
            match = re.match(r"Actuator (\d) target speed: (-?\d+\.?\d*), target length: (-?\d+\.?\d*), current length: (-?\d+\.?\d*)", line)
            if match:
                i = int(match.group(1))
                speed = float(match.group(2))
                target_length = float(match.group(3))
                current_length = float(match.group(4))

                # Update speed data
                speed_data[i].append(speed)
                # Update length data
                target_lengths[i].append(target_length)
                current_lengths[i].append(current_length)

        # Update speed lines
        for i, line in enumerate(speed_lines):
            if len(speed_data[i]) > MAX_POINTS:
                y = speed_data[i][-MAX_POINTS:]
            else:
                y = speed_data[i]
            x = list(range(len(y)))
            line.set_data(x, y)

        # Update length lines
        for i, (target_line, current_line) in enumerate(length_lines):
            if len(target_lengths[i]) > MAX_POINTS:
                y_target = target_lengths[i][-MAX_POINTS:]
            else:
                y_target = target_lengths[i]
            if len(current_lengths[i]) > MAX_POINTS:
                y_current = current_lengths[i][-MAX_POINTS:]
            else:
                y_current = current_lengths[i]  

            x_target = list(range(len(y_target)))    
            x_current = list(range(len(y_current)))
            target_line.set_data(x_target, y_target)   
            current_line.set_data(x_current, y_current)

    return speed_lines + [line for pair in length_lines for line in pair]

# ==== Save Plots After Animation Ends ====
def save_plots():
    # Save speed plots
    fig_speed, axes_speed = plt.subplots(3, 2, figsize=(12, 8))
    axes_speed = axes_speed.flatten()
    for i, ax in enumerate(axes_speed):
        ax.plot(speed_data[i], label=f'Actuator {i} Speed', color='green')
        ax.set_xlabel("Sample")
        ax.set_ylabel("Speed")
        ax.set_title(f"Actuator {i} Speeds")
        ax.legend()
        ax.grid(True)
    plt.tight_layout()
    fig_speed.savefig("Results\speeds_plot.png")
    plt.close(fig_speed)

    # Save length plots
    fig_length, axes_length = plt.subplots(3, 2, figsize=(12, 8))
    axes_length = axes_length.flatten()
    for i, ax in enumerate(axes_length):
        ax.plot(target_lengths[i], label=f'Actuator {i} Target Length', color='blue', linestyle='None', marker='o', markersize=0.1)
        ax.plot(current_lengths[i], label=f'Actuator {i} Current Length', color='orange')
        ax.set_xlabel("Sample")
        ax.set_ylabel("Length")
        ax.set_title(f"Actuator {i} Lengths")
        ax.legend()
        ax.grid(True)
    plt.tight_layout()
    fig_length.savefig("Results\lengths_plot.png")
    plt.close(fig_length)

try:
    # Start the animations
    ani = animation.FuncAnimation(fig, update, interval=200,cache_frame_data=False)
    ani2 = animation.FuncAnimation(fig2, update, interval=200, cache_frame_data=False)
    plt.tight_layout()
    plt.show()
except KeyboardInterrupt:
    print("Exiting program...")
finally:
    # Save the plots after the animation ends or on Ctrl+C
    save_plots()
    ser.close()
    print("Resources released. Program terminated.")
