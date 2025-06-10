import serial
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import serial.tools.list_ports
import re

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

# Adjust to your Teensy serial port and baudrate
SERIAL_PORT = find_teensy_port() or find_teensy_by_vid_pid()
if not SERIAL_PORT:
    raise RuntimeError("Teensy serial port not found. Please connect the Teensy and try again.")
BAUDRATE = 115200

# Pattern for actuator lines
ACTUATOR_REGEX = re.compile(
    r"(\d+)\s+Actuator 0: Length = (\d+)\s+Actuator 1: Length = (\d+)\s+"
    r"Actuator 2: Length = (\d+)\s+Actuator 3: Length = (\d+)\s+"
    r"Actuator 4: Length = (\d+)\s+Actuator 5: Length = (\d+)"
)

def main():
    print(f"Connecting to {SERIAL_PORT} at {BAUDRATE} baud...")
    ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
    buffer = []
    recording = False

    print("Waiting for 'Actuators initialized.'...")
    while True:
        line = ser.readline().decode(errors='ignore').strip()
        if not line:
            continue
        print(line)

        if "Actuators initialized." in line:
            print("✅ Recording started.")
            recording = True
            start_time = None
            continue

        if "All actuators stopped." in line and recording:
            print("🛑 Recording stopped.")
            break

        if recording:
            match = ACTUATOR_REGEX.search(line)
            if match:
                millis = int(match.group(1))
                if start_time is None:
                    start_time = millis
                elapsed = (millis - start_time) / 1000.0
                lengths = list(map(int, match.groups()[1:]))
                buffer.append((elapsed, *lengths))

    ser.close()

    if not buffer:
        print("No actuator data was recorded.")
        return

    df = pd.DataFrame(buffer, columns=["Time", "A0", "A1", "A2", "A3", "A4", "A5"])
    df.set_index("Time", inplace=True)

    # Plot
    fig, axes = plt.subplots(6, 1, figsize=(10, 14), sharex=True)
    for i in range(6):
        axes[i].plot(df.index, df[f"A{i}"], marker='o')
        axes[i].set_ylabel(f"A{i}")
        axes[i].grid(True)

    axes[-1].set_xlabel("Time (s)")
    fig.suptitle("Actuator Lengths Over Time", fontsize=16)
    plt.tight_layout(rect=[0, 0, 1, 0.97])
    plt.show()

    # Optionally save to CSV
    df.to_csv("actuator_log.csv")
    print("Data saved to 'actuator_log.csv'.")

if __name__ == "__main__":
    main()
