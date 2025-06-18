#!/usr/bin/env python3
"""
transform_chewing_filtered.py
-----------------------------

1. **Low-pass filter** head & jaw rigid-body signals *in world space*:
      - 4th-order Butterworth, zero-phase (scipy.signal.filtfilt)
2. **Transform** gnathion (jaw) pose into the head reference frame.
3. Convert the relative rotation to roll-pitch-yaw (radians, wrapped ±π).

Output CSV columns:
    Frame, Time,
    x_mm, y_mm, z_mm, roll_rad, pitch_rad, yaw_rad
"""

from __future__ import annotations
import argparse
import math
import pathlib
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from sklearn.decomposition import PCA  

# ───────────────────────────── helper functions ──────────────────────────────
def quat_to_rot(q: np.ndarray) -> np.ndarray:
    """Quaternion (x, y, z, w) → 3×3 rotation matrix."""
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

def rot_to_euler_ZYX(R: np.ndarray) -> tuple[float, float, float]:
    """Rotation matrix → (roll, pitch, yaw) radians, Z-Y-X intrinsic."""
    sy = math.hypot(R[0,0], R[1,0])
    singular = sy < 1e-6
    if not singular:
        roll  = math.atan2(R[2,1], R[2,2])
        pitch = math.atan2(-R[2,0], sy)
        yaw   = math.atan2(R[1,0], R[0,0])
    else:                       # gimbal-lock fallback
        roll  = math.atan2(-R[1,2], R[1,1])
        pitch = math.atan2(-R[2,0], sy)
        yaw   = 0.0
    return roll, pitch, yaw

wrap_rad = lambda a: (a + math.pi) % (2*math.pi) - math.pi   # → [-π, π]


# PCA helper ------------------------------------------------------------------

def compute_pca(mat: np.ndarray) -> np.ndarray:
    """Return 3 × 3 matrix whose **columns** are PCs 0, 1, 2 (desc. variance).

    Uses **sklearn.decomposition.PCA** for robustness and reproducibility.
    """
    if mat.ndim != 2 or mat.shape[1] != 3:
        raise ValueError("Expecting N×3 matrix for PCA")
    pca = PCA(n_components=3)
    pca.fit(mat)  # scikit‑learn automatically centers the data
    return pca.components_.T  # PCs as columns (shape 3×3)

# ──────────────────────────── filtering ──────────────────────────────────────
def butter_lowpass(df: pd.DataFrame, fs: float, fc: float, order: int = 4) -> pd.DataFrame:
    """Return a *new* DataFrame with Butterworth-filtered columns."""
    b, a = butter(order, fc / (fs/2), btype="low")
    out = df.copy()

    # positional triples -------------------------------------------------------
    pos_groups = [
        ["head_px", "head_py", "head_pz"],
        ["jaw_px",  "jaw_py",  "jaw_pz"],
    ]
    for cols in pos_groups:
        out[cols] = filtfilt(b, a, df[cols].values, axis=0)

    # quaternion quadruples ----------------------------------------------------
    quat_groups = [
        ["head_qx", "head_qy", "head_qz", "head_qw"],
        ["jaw_qx",  "jaw_qy",  "jaw_qz" , "jaw_qw" ],
    ]
    for cols in quat_groups:
        q = filtfilt(b, a, df[cols].values, axis=0)
        q /= np.linalg.norm(q, axis=1, keepdims=True)        # re-normalise
        out[cols] = q

    return out

# ───────────────────────── column layout (edit if Motive names differ) ───────
COLS = [
    "Frame", "Time",
    "head_qx", "head_qy", "head_qz", "head_qw", "head_px", "head_py", "head_pz",
    "jaw_qx",  "jaw_qy",  "jaw_qz",  "jaw_qw",  "jaw_px",  "jaw_py",  "jaw_pz",
]

def transform_row(row) -> list[float]:
    """World-space head & jaw → jaw expressed in head frame."""
    qh = row[["head_qx","head_qy","head_qz","head_qw"]].to_numpy()
    ph = row[["head_px","head_py","head_pz"]].to_numpy()
    qj = row[["jaw_qx","jaw_qy","jaw_qz","jaw_qw"]].to_numpy()
    pj = row[["jaw_px","jaw_py","jaw_pz"]].to_numpy()

    Rh = quat_to_rot(qh)
    Rj = quat_to_rot(qj)

    R_rel = Rh.T @ Rj                  # head → jaw rotation
    p_rel = Rh.T @ (pj - ph)           # head-frame translation (mm)

    roll, pitch, yaw = (wrap_rad(a) for a in rot_to_euler_ZYX(R_rel))
    return [*p_rel, roll, pitch, yaw]

# ────────────────────────────────── main ──────────────────────────────────────
def main(in_csv: pathlib.Path, pca_path: pathlib.Path, out_csv: pathlib.Path,
         fs: float | None, cutoff: float, order: int) -> None:

    # 1) read raw Motive export (skip 7-line header) ---------------------------
    df_raw = pd.read_csv(in_csv, header=None, names=COLS, skiprows=7)

    # 2) crop first 1 s ------------------------------------------------------
    t0 = df_raw["Time"].iloc[0]
    df_raw = df_raw[df_raw["Time"] >= t0 + 3.0].reset_index(drop=True)

    # 3) derive sampling rate if not provided ---------------------------------
    if fs is None:
        dt = df_raw["Time"].diff().median()
        if pd.isna(dt) or dt <= 0:
            raise ValueError("Cannot infer sampling rate from Time column.")
        fs = 1.0 / dt

    # 4) low-pass filter in world frame ---------------------------------------
    df_filt = butter_lowpass(df_raw, fs=fs, fc=cutoff, order=order)

    # 5) transform to head frame ----------------------------------------------
    out = df_filt[["Frame", "Time"]].copy()
    out[["x_mm","y_mm","z_mm","roll_rad","pitch_rad","yaw_rad"]] = (
        df_filt.apply(transform_row, axis=1, result_type="expand")
    )

    # 6) PCA referential -----------------------------------------------------
    if pca_path.exists():
        R_pca = np.load(pca_path)
        print(f"Loaded PCA matrix ← {pca_path}")
    else:
        coords = out[["x_mm", "y_mm", "z_mm"]].to_numpy()
        R_pca = compute_pca(coords)  # PCs 0‑2 as columns
        np.save(pca_path, R_pca)
        print(f"Saved PCA matrix → {pca_path}")

    # Build basis with (-PC2→+X, PC1→+Y, −PC0→+Z) -----------------------------
    R_basis = R_pca[:, [2, 1, 0]].copy()  # columns are new x‑y‑z axes in old coords
    R_basis[:, 0] *= -1  # flip X
    R_basis[:, 2] *= -1  # flip Z

    # Re‑express translations ------------------------------------------------
    mu = out[["x_mm", "y_mm", "z_mm"]].to_numpy().mean(axis=0)
    coords_centered = out[["x_mm", "y_mm", "z_mm"]].to_numpy() - mu
    coords_new = coords_centered @ R_basis  # N×3 matrix in PCA frame

    out["x_mm"], out["y_mm"], out["z_mm"] = [coords_new[:, i] for i in range(3)]

    # Re‑express rotations ---------------------------------------------------
    def euler_in_pca(row) -> list[float]:
        qh = row[["head_qx", "head_qy", "head_qz", "head_qw"]].to_numpy()
        qj = row[["jaw_qx", "jaw_qy", "jaw_qz", "jaw_qw"]].to_numpy()
        Rh = quat_to_rot(qh)
        Rj = quat_to_rot(qj)
        R_rel = Rh.T @ Rj  # rotation in original head frame
        R_rel_pca = R_basis.T @ R_rel @ R_basis  # in PCA frame
        return [wrap_rad(a) for a in rot_to_euler_ZYX(R_rel_pca)]

    out[["roll_rad", "pitch_rad", "yaw_rad"]] = df_filt.apply(
        euler_in_pca, axis=1, result_type="expand"
    )

    # 7) Offset to match robot origin --------------------------------
    # Take the median of the last second of data as the origin
    t1 = df_filt["Time"].iloc[-1]
    t0 = t1 - 1.0  # last second
    mask = (out["Time"] >= t0) & (out["Time"] <= t1)
    origin = out.loc[mask, ["x_mm", "y_mm", "z_mm", "roll_rad", "pitch_rad", "yaw_rad"]].median().to_numpy()
    out[["x_mm", "y_mm", "z_mm", "roll_rad", "pitch_rad", "yaw_rad"]] -= origin
    
    # save -------------------------------------------------------------------
    out.to_csv(out_csv, index=False)
    print(f"Saved → {out_csv}")


# ────────────────────────────────── CLI ───────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Jaw-in-head conversion with pre-filtering and PCA referential")
    ap.add_argument("input_csv",  type=pathlib.Path, help="Raw Motive CSV export")
    ap.add_argument("pca_path", type=pathlib.Path, help="PCA matrix (3×3) destination (.npy)")
    ap.add_argument("output_csv", type=pathlib.Path, help="Destination CSV")
    ap.add_argument("--cutoff", type=float, default=6.0,
                    help="Low-pass cut-off frequency in Hz (default 6)")
    ap.add_argument("--order", type=int, default=4,
                    help="Butterworth filter order (default 4)")
    ap.add_argument("--fs", type=float, metavar="RATE",
                    help="Sampling rate in Hz (autodetected from Time if omitted)")
    args = ap.parse_args()
    main(args.input_csv, args.pca_path, args.output_csv, fs=args.fs,
         cutoff=args.cutoff, order=args.order)
