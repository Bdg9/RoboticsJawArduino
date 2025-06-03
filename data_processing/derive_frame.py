#!/usr/bin/env python3
"""
derive_robot_frame.py  – v3
===========================

**Purpose**  Derive the fixed robot coordinate frame from one chewing‑motion
Motive CSV according to the new specification:

0. **Crop** the first 1 s (startup artefacts).
1. **Fix Z axis** → the MoCap **Y axis** (no optimisation on Z afterwards).
2. **Find Y axis**:
   * Project each jaw position onto the plane orthogonal to Z.
   * Run PCA in that plane → component with largest variance ⇒ candidate **Y**.
   * Flip sign so that `corr(Z, Y) > 0` (jaw opens ⇒ Z↓, Y↓).
3. **Compute X = Y × Z** to form a right‑handed, orthonormal basis.
4. Save the 3 × 3 rotation matrix **R_robot_from_mocap.npy** whose columns are
   (X, Y, Z) expressed in *original* MoCap coordinates.

Mathematically:
```
   v_robot = R_robot_from_mocap.T @ v_mocap
```

CLI
---
```bash
python derive_robot_frame.py run1.csv robot_frame.npy [--cutoff 6] [--order 4] [--fs RATE]
```
"""
from __future__ import annotations
import argparse
import math
import pathlib
import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from sklearn.decomposition import PCA

# ───────────────────── column layout (edit if Motive names differ) ───────────
COLS = [
    "Frame", "Time",
    "head_qx", "head_qy", "head_qz", "head_qw", "head_px", "head_py", "head_pz",
    "jaw_qx",  "jaw_qy",  "jaw_qz",  "jaw_qw",  "jaw_px",  "jaw_py",  "jaw_pz",
]

# ───────────────────────── helper: low‑pass jaw positions ────────────────────

def butter_lowpass_pos(data: np.ndarray, fs: float, fc: float, order: int = 4) -> np.ndarray:
    """Zero‑phase Butterworth filter (applied column‑wise)."""
    b, a = butter(order, fc / (fs / 2), btype="low")
    return filtfilt(b, a, data, axis=0)

# ────────────────────────────────── main ──────────────────────────────────────

def main(in_csv: pathlib.Path, out_mat: pathlib.Path,
         fs: float | None, cutoff: float, order: int):

    # 1) read Motive export (skip 7‑line header) -----------------------------
    df = pd.read_csv(in_csv, header=None, names=COLS, skiprows=7)

    # 2) crop first 1 s ------------------------------------------------------
    t0 = df["Time"].iloc[0]
    df = df[df["Time"] >= t0 + 1.0].reset_index(drop=True)

    # 3) sampling rate -------------------------------------------------------
    if fs is None:
        dt = df["Time"].diff().median()
        if pd.isna(dt) or dt <= 0:
            raise ValueError("Cannot infer sampling rate from Time column.")
        fs = 1.0 / dt

    # 4) jaw positions & filtering ------------------------------------------
    jaw_pos = df[["jaw_px", "jaw_py", "jaw_pz"]].values  # Nx3 in MoCap frame
    jaw_pos = butter_lowpass_pos(jaw_pos, fs, cutoff, order)

    # 5) define Z axis (MoCap Y) --------------------------------------------
    vZ = np.array([0.0, 1.0, 0.0])  # already unit

    # 6) project data onto plane ⟂ Z ----------------------------------------
    proj = jaw_pos - (jaw_pos @ vZ)[:, None] * vZ  # subtract Z component

    # 7) PCA in the plane to get candidate Y ---------------------------------
    pca = PCA(n_components=2)
    pca.fit(proj)               # sklearn subtracts mean automatically
    vY = pca.components_[0]     # largest variance in plane

    # ensure vY ⟂ vZ (numerical safety)
    vY -= vY.dot(vZ) * vZ
    vY /= np.linalg.norm(vY)

    # 8) choose sign: corr(Z, Y) > 0 (jaw opens ⇒ both decrease) ------------
    proj_z = jaw_pos @ vZ
    proj_y = jaw_pos @ vY
    if np.corrcoef(proj_z, proj_y)[0, 1] < 0:
        vY = -vY

    # 9) compute X = Y × Z ----------------------------------------------------
    vX = np.cross(vY, vZ)
    vX /= np.linalg.norm(vX)

    # 10) build rotation matrix (columns = X,Y,Z) ----------------------------
    R_robot_from_mocap = np.column_stack((vX, vY, vZ))

    # sanity: right‑handed & orthonormal
    if not np.isclose(np.linalg.det(R_robot_from_mocap), 1.0, atol=1e-3):
        raise ValueError("Resulting basis not right‑handed/orthonormal – check data.")

    # 11) save ---------------------------------------------------------------
    np.save(out_mat, R_robot_from_mocap)
    print("Rotation matrix saved to", out_mat)
    print("R_robot_from_mocap (X Y Z columns in MoCap frame):\n", R_robot_from_mocap)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Derive robot frame with fixed Z=MoCap‑Y and PCA for Y")
    ap.add_argument("input_csv", type=pathlib.Path, help="CSV with chewing motion (Motive export)")
    ap.add_argument("frame_matrix", type=pathlib.Path, help="Output .npy for 3×3 rotation matrix")
    ap.add_argument("--cutoff", type=float, default=6.0, help="Low‑pass cut‑off frequency Hz (default 6)")
    ap.add_argument("--order", type=int, default=4, help="Butterworth filter order (default 4)")
    ap.add_argument("--fs", type=float, metavar="RATE", help="Sampling rate Hz (autodetect if omitted)")
    args = ap.parse_args()
    main(args.input_csv, args.frame_matrix, fs=args.fs, cutoff=args.cutoff, order=args.order)
