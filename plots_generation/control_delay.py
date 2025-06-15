#!/usr/bin/env python3
"""
delay_xcorr.py  –  Estimate commanded-vs-measured delay per actuator
Usage:
    python delay_xcorr.py data.csv
Dependencies:
    pip install pandas numpy scipy
"""
import sys
import numpy as np
import pandas as pd
from scipy.signal import correlate, correlation_lags

def normalised_xcorr(x, y):
    """Return full, zero-mean, unit-variance cross-correlation ρ_xy(k)."""
    x = x - x.mean()
    y = y - y.mean()
    denom = np.sqrt(np.sum(x**2) * np.sum(y**2))
    return correlate(y, x, mode='full') / denom           # +lag ⇒ y lags x

def analyse_actuator(df_act):
    u = df_act["target_length"].to_numpy()
    y = df_act["current_length"].to_numpy()
    rho = normalised_xcorr(u, y)
    lags = correlation_lags(len(y), len(u), mode='full')  # same length as rho
    k_peak = int(lags[np.argmax(np.abs(rho))])            # lag (samples)
    rho_peak = float(rho[np.argmax(np.abs(rho))])

    # Estimate Δt from the 'time' column (assumes monotonic ascending)
    t = df_act["time"].to_numpy()
    dt = np.median(np.diff(t)) if len(t) > 1 else np.nan
    print(f"Actuator {df_act['actuator'].iloc[0]}: dt = {dt:.6f} s, k_peak = {k_peak}")
    tau_sec = k_peak * dt

    return k_peak, tau_sec, rho_peak

def main(csv_path):
    df = pd.read_csv(csv_path)
    required = {"actuator", "target_length", "current_length", "time"}
    if not required.issubset(df.columns):
        sys.exit(f"CSV must contain columns: {', '.join(required)}")

    pose_df = pd.read_csv(csv_path.replace("actuator", "pose"))
    #extract first non-zero pose time
    first_non_zero_time = pose_df[pose_df.iloc[:, :6].ne(0).any(axis=1)]['time'].iloc[0]
    #extract last non-zero pose time
    last_non_zero_time = pose_df[pose_df.iloc[:, :6].ne(0).any(axis=1)]['time'].iloc[-1]
    # Crop the actuator data to the first non-zero pose time
    df = df[(df['time'] >= first_non_zero_time) & (df['time'] <= last_non_zero_time)]

    print("\nCross-correlation delay per actuator")
    print("------------------------------------")
    for act_id, group in df.groupby("actuator"):
        k, tau, rho = analyse_actuator(group)
        direction = "y lags u" if k > 0 else "u lags y" if k < 0 else "no lag"
        tau_ms = tau * 1e3
        print(f"Actuator {act_id}: lag = {k:+d} samples  "
              f"({tau_ms/1000:+.2f} ms, {direction})   ρ = {rho:+.4f}")

actuator_path_names = ["../Results/benhui_10s_40ms/benhui_gum_10s_40_ms_actuator_data_20250613-182908.csv",
            "../Results/benhui_10s_50ms/benhui_gum_10s_50_ms_actuator_data_20250613-182743.csv",
            "../Results/benhui_10s_60ms/benhui_gum_10s_60_ms_actuator_data_20250613-193131.csv",
            "../Results/benhui_10s_70ms/benhui_gum_10s_70_ms_actuator_data_20250613-182602.csv",
            "../Results/benhui_10s_80ms/benhui_gum_10s_80_ms_actuator_data_20250613-183103.csv",
            "../Results/benhui_10s_90ms/benhui_gum_10s_90_ms_actuator_data_20250613-182359.csv",
            "../Results/benhui_10s_100ms/benhui_gum_10s_100_ms_actuator_data_20250613-182110.csv"]
    
for actuator_path in actuator_path_names:
    print(f"\nProcessing {actuator_path}")
    main(actuator_path)
