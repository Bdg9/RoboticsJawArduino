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
    tau_sec = k_peak * dt

    return k_peak, tau_sec, rho_peak

def main(csv_path):
    df = pd.read_csv(csv_path)
    required = {"actuator", "target_length", "current_length", "time"}
    if not required.issubset(df.columns):
        sys.exit(f"CSV must contain columns: {', '.join(required)}")

    print("\nCross-correlation delay per actuator")
    print("------------------------------------")
    for act_id, group in df.groupby("actuator"):
        k, tau, rho = analyse_actuator(group)
        direction = "y lags u" if k > 0 else "u lags y" if k < 0 else "no lag"
        tau_ms = tau * 1e3
        print(f"Actuator {act_id}: lag = {k:+d} samples  "
              f"({tau_ms:+.2f} ms, {direction})   ρ = {rho:+.4f}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python delay_xcorr.py <file.csv>")
    main(sys.argv[1])
