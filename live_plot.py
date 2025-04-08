# pip install pyserial matplotlib 

import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import re
import time
import serial.tools.list_ports

# ==== Helper Functions ====

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

def update_line(line, x_data, y_data):
    if len(y_data) > MAX_POINTS:
        x = x_data[-MAX_POINTS:]
        y = y_data[-MAX_POINTS:]
    else:
        x = x_data
        y = y_data
    if len(x) > 0:
        x = [i - x[0] for i in x]  # Normalize x-axis to start from 0
    line.set_data(x, y)

def save_plot(fig, axes, data, titles, y_labels, filename):
    for ax, title, y_label, values in zip(axes, titles, y_labels, data):
        ax.plot(values, label=title)
        ax.set_xlabel("Sample")
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.legend()
        ax.grid(True)
    plt.tight_layout()
    fig.savefig(filename)
    plt.close(fig)

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
timestamps = {i: [] for i in range(6)}  # Timestamps for actuators
pose_data = {
    "x": [],
    "y": [],
    "z": [],
    "roll": [],
    "pitch": [],
    "yaw": [],
    "timestamp": [],
}

# ==== Set up Serial ====
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(2)  # Let the Teensy reset
start_time = time.time()

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

# ==== Setup Plot for Pose ====
fig3, axes3 = plt.subplots(3, 2, figsize=(12, 8))  # Create a 3x2 grid of subplots for pose
axes3 = axes3.flatten()  # Flatten the 2D array of axes for easier indexing
pose_lines = {}

# Define y-axis limits for each pose component
pose_limits = {
    "x": (-20, 20),
    "y": (-20, 20),
    "z": (375, 481),
    "roll": (-1.5, 1.5),  # -π/2 to π/2
    "pitch": (-1.5, 1.5),  # -π/2 to π/2
    "yaw": (-1.5, 1.5),  # -π/2 to π/2
}

for i, (key, ax) in enumerate(zip(pose_data.keys(), axes3)):
    line, = ax.plot([], [], label=f'{key.capitalize()}')
    pose_lines[key] = line
    ax.set_xlim(0, MAX_POINTS)
    ax.set_ylim(*pose_limits[key])  # Set y-axis limits based on the pose component
    ax.set_xlabel("Sample")
    ax.set_ylabel(key.capitalize())
    ax.set_title(f"Pose {key.capitalize()}")
    ax.legend()
    ax.grid(True)

# ==== Animation Update Function ====
def update(frame):
    for _ in range(500):  # Process up to 500 lines per frame
        if ser.in_waiting:
            line = ser.readline().decode(errors='ignore').strip()
            current_time = time.time()-start_time
            match = re.match(r"Actuator (\d) target speed: (-?\d+\.?\d*), target length: (-?\d+\.?\d*), current length: (-?\d+\.?\d*), time: (-?\d+\.?\d*)", line)
            if match:
                i = int(match.group(1))
                speed = float(match.group(2))
                target_length = float(match.group(3))
                current_length = float(match.group(4))
                timestamp = float(match.group(5))

                # Update speed data
                speed_data[i].append(speed)
                # Update length data
                target_lengths[i].append(target_length)
                current_lengths[i].append(current_length)
                # Update timestamps
                timestamps[i].append(timestamp)
            
            match = re.match(r"Pose: x: (-?\d+\.?\d*), y: (-?\d+\.?\d*), z: (-?\d+\.?\d*), roll: (-?\d+\.?\d*), pitch: (-?\d+\.?\d*), yaw: (-?\d+\.?\d*), time: (-?\d+\.?\d*)", line)
            if match:
                pose_data["x"].append(float(match.group(1)))
                pose_data["y"].append(float(match.group(2)))
                pose_data["z"].append(float(match.group(3)))
                pose_data["roll"].append(float(match.group(4)))
                pose_data["pitch"].append(float(match.group(5)))
                pose_data["yaw"].append(float(match.group(6)))
                pose_data["timestamp"].append(float(match.group(7)))

        # Update speed lines
        for i, line in enumerate(speed_lines):
            update_line(line, timestamps[i], speed_data[i])

        # Update length lines
        for i, (target_line, current_line) in enumerate(length_lines):
            update_line(target_line, timestamps[i], target_lengths[i])
            update_line(current_line, timestamps[i], current_lengths[i])
        
        #update pose lines
        for i, (key, line) in enumerate(pose_lines.items()):
            if key != "timestamp":
                update_line(line, pose_data["timestamp"], pose_data[key])

        # Update x-axis limits for all plots
        for i, line in enumerate(speed_lines):
            x_data = line.get_xdata()
            if len(x_data) > 0:
                    axes[i].set_xlim(x_data[0], x_data[-1])

        for i, (target_line, current_line) in enumerate(length_lines):
            x_data_target = target_line.get_xdata()
            x_data_current = current_line.get_xdata()
            if len(x_data_target) > 1:
                axes2[i].set_xlim(x_data_target[0], x_data_target[-1])

        x_data_pose = list(pose_lines.values())[0].get_xdata()  # Use the first pose line for x-axis limits
        if len(x_data_pose) > 1:
            for ax in axes3:
                ax.set_xlim(x_data_pose[0], x_data_pose[-1])

    return speed_lines + [line for pair in length_lines for line in pair] + list(pose_lines.values())

# ==== Save Plots After Animation Ends ====
def save_plots():
    # Save speed plots
    fig_speed, axes_speed = plt.subplots(3, 2, figsize=(12, 8))
    axes_speed = axes_speed.flatten()
    for i, ax in enumerate(axes_speed):
        timestamps[i] = [t - timestamps[i][0] for t in timestamps[i]]  # Normalize timestamps to start from 0

        ax.plot(timestamps[i], speed_data[i], label=f'Motor speed command', color='green')
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
        timestamps[i] = [t - timestamps[i][0] for t in timestamps[i]]  # Normalize timestamps to start from 0
        ax.plot(timestamps[i], target_lengths[i], label=f'Target Length', color='blue', linestyle='None', marker='o', markersize=0.1)
        ax.plot(timestamps[i], current_lengths[i], label=f'Current Length', color='orange')
        ax.set_xlabel("Sample")
        ax.set_ylabel("Length")
        ax.set_title(f"Actuator {i} Lengths")
        ax.legend()
        ax.grid(True)
    plt.tight_layout()
    fig_length.savefig("Results\lengths_plot.png")
    plt.close(fig_length)

    fig_pose, axes_pose = plt.subplots(3, 2, figsize=(12, 8))
    axes_pose = axes_pose.flatten()
    for i, (key, ax) in enumerate(zip(pose_data.keys(), axes_pose)):
        if key != "timestamp":
            pose_data["timestamp"] = [t - pose_data["timestamp"][0] for t in pose_data["timestamp"]]  # Normalize timestamps to start from 0
            ax.plot(pose_data["timestamp"], pose_data[key], label=f'{key.capitalize()}', color='purple', linestyle='None', marker='o', markersize=0.1)
            ax.set_xlabel("Sample")
            ax.set_ylabel(key.capitalize())
            ax.set_title(f"{key.capitalize()}")
            ax.legend()
            ax.grid(True)
    plt.tight_layout()
    fig_pose.savefig("Results\pose_plot.png")
    plt.close(fig_pose)

try:
    # Start the animations
    ani = animation.FuncAnimation(fig, update, interval=200,cache_frame_data=False)
    ani2 = animation.FuncAnimation(fig2, update, interval=200, cache_frame_data=False)
    ani3 = animation.FuncAnimation(fig3, update, interval=200, cache_frame_data=False)

    plt.tight_layout()
    plt.show()
except KeyboardInterrupt:
    print("Exiting program...")
finally:
    # Save the plots after the animation ends or on Ctrl+C
    save_plots()
    ser.close()
    print("Resources released. Program terminated.")
