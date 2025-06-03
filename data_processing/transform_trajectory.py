#!/usr/bin/env python3
"""
transform_trajectory.py
-----------------------

Apply a previously computed robot‑frame rotation matrix to one or more chewing
trajectories so that positions and orientations are expressed in the robot
coordinate system.

Input
~~~~~
* 3×3 matrix ``frame_matrix.npy`` created with *derive_robot_frame.py*
* Raw Motive CSV export(s)

Output
~~~~~~
CSV with columns::

    Frame, Time,
    x_mm, y_mm, z_mm, roll_rad, pitch_rad, yaw_rad

Each row represents the gnathion pose relative to the head rigid body,
expressed in the robot frame.
"""
from __future__ import annotations
import argparse
import math
import pathlib
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt

# ───────────────────────────── helper functions ──────────────────────────────
COLS = [
    "Frame", "Time",
    "head_qx", "head_qy", "head_qz", "head_qw", "head_px", "head_py", "head_pz",
    "jaw_qx",  "jaw_qy",  "jaw_qz",  "jaw_qw",  "jaw_px",  "jaw_py",  "jaw_pz",
]

def quat_to_rot(q: np.ndarray) -> np.ndarray:
    x, y, z, w = q
    n = math.sqrt(x*x + y*y + z*z + w*w)
    if n == 0:
        raise ValueError("Zero‑norm quaternion")
    x, y, z, w = x/n, y/n, z/n, w/n
    return np.array([
        [1 - 2*(y*y + z*z),     2*(x*y - z*w),       2*(x*z + y*w)],
        [    2*(x*y + z*w), 1 - 2*(x*x + z*z),       2*(y*z - x*w)],
        [    2*(x*z - y*w),     2*(y*z + x*w),   1 - 2*(x*x + y*y)]
    ])

def rot_to_euler_ZYX(R: np.ndarray):
    sy = math.hypot(R[0, 0], R[1, 0])
    singular = sy < 1e-6
    if not singular:
        roll  = math.atan2(R[2, 1], R[2, 2])
        pitch = math.atan2(-R[2, 0], sy)
        yaw   = math.atan2(R[1, 0], R[0, 0])
    else:
        roll  = math.atan2(-R[1, 2], R[1, 1])
        pitch = math.atan2(-R[2, 0], sy)
        yaw   = 0.0
    return roll, pitch, yaw

wrap_rad = lambda a: (a + math.pi) % (2*math.pi) - math.pi

def butter_lowpass(df: pd.DataFrame, fs: float, fc: float, order: int = 4) -> pd.DataFrame:
    b, a = butter(order, fc / (fs/2), btype="low")
    out = df.copy()
    pos_cols = [["head_px", "head_py", "head_pz"], ["jaw_px", "jaw_py", "jaw_pz"]]
    quat_cols = [["head_qx", "head_qy", "head_qz", "head_qw"], ["jaw_qx", "jaw_qy", "jaw_qz", "jaw_qw"]]
    for cols in pos_cols:
        out[cols] = filtfilt(b, a, df[cols].values, axis=0)
    for cols in quat_cols:
        q = filtfilt(b, a, df[cols].values, axis=0)
        q /= np.linalg.norm(q, axis=1, keepdims=True)
        out[cols] = q
    return out

# ────────────────────────────────── main ──────────────────────────────────────

def main(in_csv: pathlib.Path, mat_file: pathlib.Path, out_csv: pathlib.Path,
         fs: float | None, cutoff: float, order: int):
    R_robot_from_mocap = np.load(mat_file)
    if R_robot_from_mocap.shape != (3, 3):
        raise ValueError("Rotation matrix must be 3×3")
    Rt = R_robot_from_mocap.T  # transpose once for speed

    df_raw = pd.read_csv(in_csv, header=None, names=COLS, skiprows=7)

    if fs is None:
        dt = df_raw["Time"].diff().median()
        if pd.isna(dt) or dt <= 0:
            raise ValueError("Cannot infer sampling rate from Time column.")
        fs = 1.0 / dt

    df_filt = butter_lowpass(df_raw, fs=fs, fc=cutoff, order=order)

    def transform_row(row):
        qh = row[["head_qx", "head_qy", "head_qz", "head_qw"]].to_numpy()
        ph = row[["head_px", "head_py", "head_pz"]].to_numpy()
        qj = row[["jaw_qx",  "jaw_qy",  "jaw_qz",  "jaw_qw"]].to_numpy()
        pj = row[["jaw_px",  "jaw_py",  "jaw_pz"]].to_numpy()

        Rh = quat_to_rot(qh)
        Rj = quat_to_rot(qj)

        R_rel_head = Rh.T @ Rj
        p_rel_head = Rh.T @ (pj - ph)

        R_rel_robot = Rt @ R_rel_head
        p_rel_robot = Rt @ p_rel_head

        roll, pitch, yaw = (wrap_rad(a) for a in rot_to_euler_ZYX(R_rel_robot))
        return [*p_rel_robot, roll, pitch, yaw]

    out = df_filt[["Frame", "Time"]].copy()
    out[["x_mm", "y_mm", "z_mm", "roll_rad", "pitch_rad", "yaw_rad"]] = (
        df_filt.apply(transform_row, axis=1, result_type="expand")
    )

    out.to_csv(out_csv, index=False)
    print("Saved →", out_csv)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Transform trajectories to robot frame using saved matrix")
    ap.add_argument("input_csv", type=pathlib.Path, help="Raw Motive CSV export to transform")
    ap.add_argument("frame_matrix", type=pathlib.Path, help=".npy file from derive_robot_frame.py")
    ap.add_argument("output_csv", type=pathlib.Path, help="Destination CSV")
    ap.add_argument("--cutoff", type=float, default=6.0, help="Low‑pass cut‑off frequency Hz (default 6)")
    ap.add_argument("--order", type=int, default=4, help="Butterworth filter order (default 4)")
    ap.add_argument("--fs", type=float, metavar="RATE", help="Sampling rate Hz (autodetect if omitted)")
    args = ap.parse_args()
    main(args.input_csv, args.frame_matrix, args.output_csv,
         fs=args.fs, cutoff=args.cutoff, order=args.order)
