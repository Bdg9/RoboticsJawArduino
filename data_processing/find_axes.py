import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from matplotlib.animation import FuncAnimation, FFMpegWriter

def mocap_to_robot_frame(pos, rot_matrix):
    """
    Converts from MoCap frame to robot frame.
    Mapping:
        mocap X → robot X
        mocap Y → robot Z
        mocap Z → robot Y
    Equivalent to permuting axes.
    """
    # Remap position
    pos_robot = np.array([pos[0], pos[2], pos[1]])

    # Remap rotation matrix columns (same as permuting axes)
    R_robot = np.zeros((3, 3))
    R_robot[:, 0] = rot_matrix[:, 0]               # X stays X
    R_robot[:, 1] = rot_matrix[:, 2]               # Z becomes Y
    R_robot[:, 2] = rot_matrix[:, 1]               # Y becomes Z
    return pos_robot, R_robot

def plot_frame(ax, origin, R_matrix, label, length=20):
    """Plot a 3D frame with arrows for x (red), y (green), z (blue)"""
    colors = ['r', 'g', 'b']
    for i in range(3):
        axis = R_matrix[:, i] * length
        ax.quiver(
            origin[0], origin[1], origin[2],
            axis[0], axis[1], axis[2],
            color=colors[i],
            linewidth=1,
            alpha=0.6 if i > 0 else 1.0,  # make x axis more visible
            label=f'{label} {"XYZ"[i]}' if i == 0 else None
        )


COLS = [
"Frame", "Time",
"head_qx", "head_qy", "head_qz", "head_qw", "head_px", "head_py", "head_pz",
"jaw_qx",  "jaw_qy",  "jaw_qz",  "jaw_qw",  "jaw_px",  "jaw_py",  "jaw_pz",
]

# Load your CSV (replace with your actual file)
df = pd.read_csv('data\Take_2025-05-02_02.32.17_PM.csv', header=None, names=COLS, skiprows=208)

num_frames = min(200, len(df))

#fid axis limits based on df data
x_min_head = df['head_px'].min()
x_max_head = df['head_px'].max()
z_min_head = df['head_py'].min()
z_max_head = df['head_py'].max()
y_min_head = df['head_pz'].min()
y_max_head = df['head_pz'].max()
x_min_jaw = df['jaw_px'].min()
x_max_jaw = df['jaw_px'].max()
z_min_jaw = df['jaw_py'].min()
z_max_jaw = df['jaw_py'].max()
y_min_jaw = df['jaw_pz'].min()
y_max_jaw = df['jaw_pz'].max()
x_min = min(x_min_head, x_min_jaw) - 20
x_max = max(x_max_head, x_max_jaw) + 20
y_min = min(y_min_head, y_min_jaw) - 20
y_max = max(y_max_head, y_max_jaw) + 20
z_min = min(z_min_head, z_min_jaw) - 20
z_max = max(z_max_head, z_max_jaw) + 20

# Preprocess data
frames = []
for i in range(num_frames):
    row = df.iloc[i]

    head_pos = np.array([row['head_px'], row['head_py'], row['head_pz']])
    head_quat = np.array([row['head_qx'], row['head_qy'], row['head_qz'], row['head_qw']])
    head_rot = R.from_quat(head_quat).as_matrix()
    head_pos_robot, head_rot_robot = mocap_to_robot_frame(head_pos, head_rot)

    jaw_pos = np.array([row['jaw_px'], row['jaw_py'], row['jaw_pz']])
    jaw_quat = np.array([row['jaw_qx'], row['jaw_qy'], row['jaw_qz'], row['jaw_qw']])
    jaw_rot = R.from_quat(jaw_quat).as_matrix()
    jaw_pos_robot, jaw_rot_robot = mocap_to_robot_frame(jaw_pos, jaw_rot)

    frames.append((head_pos_robot, head_rot_robot, jaw_pos_robot, jaw_rot_robot))

# Setup 3D figure
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
ax.set_title('Head and Jaw Animation (Robot Frame)')
ax.set_xlabel('Robot X')
ax.set_ylabel('Robot Y')
ax.set_zlabel('Robot Z')

# Set axis limits based on first pose
ref = frames[0][0]
ax.set_xlim([x_min, x_max])
ax.set_ylim([y_min, y_max])
ax.set_zlim([z_min, z_max])

quivers = []

def init():
    return []

def update(i):
    global quivers
    for q in quivers:
        q.remove()
    quivers = []

    head_pos, head_rot, jaw_pos, jaw_rot = frames[i]
    for j in range(3):
        axis = head_rot[:, j] * 20
        quivers.append(ax.quiver(*head_pos, *axis, color='rbg'[j]))
        axis = jaw_rot[:, j] * 20
        quivers.append(ax.quiver(*jaw_pos, *axis, color='rbg'[j]))

    return quivers

ani = FuncAnimation(fig, update, frames=num_frames, init_func=init, blit=False, interval=100)

# Save to MP4 (optional)
ani.save('head_jaw_animation.mp4', writer=FFMpegWriter(fps=10))

# Or show live
# plt.show()