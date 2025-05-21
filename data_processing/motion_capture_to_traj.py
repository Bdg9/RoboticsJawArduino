#!/usr/bin/env python3
"""
Transform gnathion (jaw) marker coordinates into the head reference frame
and convert quaternion orientation into (x , y , z , roll , pitch , yaw).

• x, y, z  in millimetres
• roll, pitch, yaw  in radians  (wrapped to [-π, π])
"""

import argparse
import math
import pathlib
import numpy as np
import pandas as pd

# ───────────────────────────── helper functions ──────────────────────────────
def quat_to_rot(q):
    """Quaternion (x, y, z, w) → 3 × 3 rotation matrix."""
    x, y, z, w = q
    n = math.sqrt(x*x + y*y + z*z + w*w)
    if n == 0:
        raise ValueError("Zero-norm quaternion")
    x, y, z, w = x/n, y/n, z/n, w/n
    return np.array([
        [1-2*(y*y+z*z),   2*(x*y - z*w), 2*(x*z + y*w)],
        [2*(x*y + z*w), 1-2*(x*x+z*z),   2*(y*z - x*w)],
        [2*(x*z - y*w),   2*(y*z + x*w), 1-2*(x*x+y*y)]
    ])

def rot_to_euler_ZYX(R):
    """
    Rotation matrix → (roll, pitch, yaw) **in radians**
    following Z-Y-X (yaw-pitch-roll) intrinsic convention.
    """
    sy = math.hypot(R[0,0], R[1,0])
    singular = sy < 1e-6
    if not singular:
        roll  = math.atan2(R[2,1], R[2,2])
        pitch = math.atan2(-R[2,0], sy)
        yaw   = math.atan2(R[1,0], R[0,0])
    else:  # gimbal-lock fallback
        roll  = math.atan2(-R[1,2], R[1,1])
        pitch = math.atan2(-R[2,0], sy)
        yaw   = 0.0
    return roll, pitch, yaw

# CHANGED: wrap to [-π, π] **without converting to degrees**
wrap_rad = lambda a: (a + math.pi) % (2*math.pi) - math.pi

# ───────────────────────── column layout (adjust if needed) ───────────────────
COLS = [
    'Frame','Time',
    'head_qx','head_qy','head_qz','head_qw','head_px','head_py','head_pz',
    'jaw_qx', 'jaw_qy', 'jaw_qz', 'jaw_qw', 'jaw_px','jaw_py','jaw_pz'
]

def transform_row(row):
    qh = np.array([row['head_qx'], row['head_qy'], row['head_qz'], row['head_qw']])
    ph = np.array([row['head_px'], row['head_py'], row['head_pz']])
    qj = np.array([row['jaw_qx'],  row['jaw_qy'],  row['jaw_qz'],  row['jaw_qw']])
    pj = np.array([row['jaw_px'],  row['jaw_py'],  row['jaw_pz']])

    Rh = quat_to_rot(qh)          # world → head
    Rj = quat_to_rot(qj)          # world → jaw

    R_rel = Rh.T @ Rj             # head → jaw orientation
    p_rel = Rh.T @ (pj - ph)      # translation in head frame (mm)

    roll, pitch, yaw = (wrap_rad(x) for x in rot_to_euler_ZYX(R_rel))
    return *p_rel, roll, pitch, yaw

# ────────────────────────────────── main ──────────────────────────────────────
def main(in_csv: pathlib.Path, out_csv: pathlib.Path):
    # OptiTrack/Motive CSV: 7-row preamble, then numeric data
    df = pd.read_csv(in_csv, header=None, names=COLS, skiprows=7)
    out = df[['Frame', 'Time']].copy()

    # CHANGED: column names now end with _rad
    out[['x_mm', 'y_mm', 'z_mm', 'roll_rad', 'pitch_rad', 'yaw_rad']] = (
        df.apply(transform_row, axis=1, result_type='expand')
    )
    out.to_csv(out_csv, index=False)
    print(f"Saved → {out_csv}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Jaw-in-head frame conversion")
    ap.add_argument("input_csv",  type=pathlib.Path, help="Raw Motive export")
    ap.add_argument("output_csv", type=pathlib.Path, help="Destination CSV")
    args = ap.parse_args()
    main(args.input_csv, args.output_csv)
