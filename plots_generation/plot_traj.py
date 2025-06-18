import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

file_path = "../data_processing/benhui_gum_random_10s_inverted.csv"
df = pd.read_csv(file_path)

#make a time column at 120Hz
df["time"] = np.arange(len(df)) / 120.0 # Assuming 120Hz sampling rate

#convert angles from radians to degrees
df["roll_deg"] = np.rad2deg(df["roll_rad"])
df["pitch_deg"] = np.rad2deg(df["pitch_rad"])
df["yaw_deg"] = np.rad2deg(df["yaw_rad"])

#only keep the first 4s
df = df[df["time"] <= 4.0].reset_index(drop=True)

#plot the trajectory
fig, axs = plt.subplots(6, 1, figsize=(15, 10), sharex=True)
axs[0].plot(df["time"], df["x_mm"], label="x")
axs[1].plot(df["time"], df["y_mm"], label="y")
axs[2].plot(df["time"], df["z_mm"], label="z")
axs[3].plot(df["time"], df["roll_deg"], label="roll")
axs[4].plot(df["time"], df["pitch_deg"], label="pitch")
axs[5].plot(df["time"], df["yaw_deg"], label="yaw")
axs[0].set_ylabel("X Position (mm)")
axs[1].set_ylabel("Y Position (mm)")
axs[2].set_ylabel("Z Position (mm)")
axs[3].set_ylabel("Roll (degrees)")
axs[4].set_ylabel("Pitch (degrees)")
axs[5].set_ylabel("Yaw (degrees)")
axs[5].set_xlabel("Time (s)")
for ax in axs:
    ax.grid()
plt.tight_layout()
plt.savefig("trajectory_plot.png", dpi=300)
plt.close('all')

plt.figure(figsize=(3, 6))
plt.plot(df["y_mm"], df["z_mm"], label="X Position (mm)")
#have the same scale for both axes
plt.xlabel("Y Position (mm)")
plt.ylabel("Z Position (mm)")
plt.axis('scaled')
plt.grid()
plt.tight_layout()
plt.savefig("y_vs_z_position.png", dpi=300)

plt.figure(figsize=(3, 6))
plt.plot(df["x_mm"], df["z_mm"], label="Y Position (mm)")
plt.xlabel("X Position (mm)")
plt.ylabel("Z Position (mm)")
plt.grid()
plt.axis('scaled')
plt.tight_layout()
plt.savefig("x_vs_z_position.png", dpi=300)
