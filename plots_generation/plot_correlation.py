import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import correlate, correlation_lags


def normalised_xcorr(x, y):
    x = x - x.mean()
    y = y - y.mean()
    denom = np.sqrt(np.sum(x**2) * np.sum(y**2))
    return correlate(y, x, mode='full') / denom

def rms_error_shifted(u: np.ndarray, y: np.ndarray, k: int) -> float:
    """Return RMS(|shift(u,k) − y|) after aligning for lag k.

    Positive *k* means *y* lags *u*, so we discard the first *k* samples of *u*.
    Negative *k* means *u* lags *y*, so we discard the first |k| samples of *y*.
    """
    if k > 0:
        # Discard the first *k* samples of u so that u[k] aligns with y[0]
        u_aligned = u[k:]
        y_aligned = y[: len(u_aligned)]
    elif k < 0:
        k_abs = abs(k)
        # Discard first |k| samples of y so that y[k_abs] aligns with u[0]
        y_aligned = y[k_abs:]
        u_aligned = u[: len(y_aligned)]
    else:
        u_aligned = u
        y_aligned = y

    if len(u_aligned) == 0 or len(y_aligned) == 0:
        return np.nan

    return float(np.sqrt(np.mean((u_aligned - y_aligned) ** 2)))


def analyse_actuator(df_act):
    u = df_act["target_length"].to_numpy()
    y = df_act["current_length"].to_numpy()
    rho = normalised_xcorr(u, y)
    lags = correlation_lags(len(y), len(u), mode='full')
    k_peak = int(lags[np.argmax(np.abs(rho))])
    rho_peak = float(rho[np.argmax(np.abs(rho))])

    t = df_act["time"].to_numpy()
    dt = np.median(np.diff(t)) if len(t) > 1 else np.nan

    tau_sec = k_peak * dt
    # RMS error after delay compensation
    rms_err = rms_error_shifted(u, y, k_peak)
    return k_peak, tau_sec * 1e3, rho_peak, rms_err  # return delay in ms


def process_file(csv_path):
    df = pd.read_csv(csv_path)
    pose_df = pd.read_csv(csv_path.replace("actuator", "pose"))

    first_non_zero_time = pose_df[pose_df.iloc[:, :6].ne(0).any(axis=1)]["time"].iloc[0]
    last_non_zero_time = pose_df[pose_df.iloc[:, :6].ne(0).any(axis=1)]["time"].iloc[-1]
    df = df[(df["time"] >= first_non_zero_time) & (df["time"] <= last_non_zero_time)]

    delays = []
    rhos = []
    rms_errors = []
    for act_id, group in df.groupby("actuator"):
        k, tau_ms, rho, rms = analyse_actuator(group)
        tau_ms = tau_ms / 1e3  # convert to milliseconds
        delays.append(tau_ms)
        rhos.append(rho)
        rms_errors.append(rms)
    
    return delays, rhos, rms_errors


def plot_results(time_intervals, delay_data, rho_data, rms_data):    
    df_delay = pd.DataFrame(delay_data, index=time_intervals)
    df_rho = pd.DataFrame(rho_data, index=time_intervals)
    df_rms = pd.DataFrame(rms_data, index=time_intervals)

    delay_mean = df_delay.mean(axis=1).to_numpy()
    delay_std = df_delay.std(axis=1).to_numpy()
    rho_mean = df_rho.mean(axis=1).to_numpy()
    rho_std = df_rho.std(axis=1).to_numpy()
    rms_mean = df_rms.mean(axis=1).to_numpy()
    rms_std = df_rms.std(axis=1).to_numpy()
    x_vals = np.array(time_intervals, dtype=float)

    # Plot delay
    plt.figure(figsize=(10, 6))
    for column in df_delay.columns:
        plt.plot(x_vals, df_delay[column], linestyle='--', alpha=0.5, label=f'Actuator {column}')
    plt.plot(x_vals, delay_mean, color='black', marker='o', label='Mean Delay')
    plt.fill_between(x_vals, delay_mean - delay_std, delay_mean + delay_std, color='gray', alpha=0.3, label='±1 Std Dev')
    plt.xlabel("Time Interval Between Trajectory Points (ms)")
    plt.ylabel("Delay (ms)")
    plt.grid(True)
    plt.gca().invert_xaxis()
    plt.legend()
    plt.tight_layout()
    plt.savefig("actuator_delays.png", dpi=300)

    # Plot rho
    plt.figure(figsize=(10, 6))
    for column in df_rho.columns:
        plt.plot(x_vals, df_rho[column], linestyle='--', alpha=0.5, label=f'Actuator {column}')
    plt.plot(x_vals, rho_mean, color='black', marker='o', label='Mean ρ')
    plt.fill_between(x_vals, rho_mean - rho_std, rho_mean + rho_std, color='gray', alpha=0.3, label='±1 Std Dev')
    plt.xlabel("Time Interval Between Trajectory Points (ms)")
    plt.ylabel("Cross-Correlation ρ")
    plt.grid(True)
    plt.gca().invert_xaxis()
    plt.ylim(0.8, 1.0)
    plt.legend()
    plt.tight_layout()
    plt.savefig("actuator_rhos.png", dpi=300)

    # Plot RMS error
    plt.figure(figsize=(10, 6))
    for column in df_rms.columns:
        plt.plot(x_vals, df_rms[column], linestyle='--', alpha=0.5, label=f'Actuator {column}')
    plt.plot(x_vals, rms_mean, color='black', marker='o', label='Mean RMS Error')
    plt.fill_between(x_vals, rms_mean - rms_std, rms_mean + rms_std, color='gray', alpha=0.3, label='±1 Std Dev')
    # add the values of the mean RMS error on the plot
    # for i, val in enumerate(rms_mean):
    #     plt.text(x_vals[i], val + 0.1, f"{val:.2f}", ha='center', va='bottom', fontsize=8)
    plt.xlabel("Time Interval Between Trajectory Points (ms)")
    plt.ylabel("RMS Error (mm)")
    plt.grid(True)
    plt.gca().invert_xaxis()
    plt.legend()
    plt.tight_layout()
    plt.savefig("actuator_rms_errors.png", dpi=300)


if __name__ == "__main__":
    actuator_path_names = [
        "../Results/benhui_10s_40ms/benhui_gum_10s_40_ms_actuator_data_20250613-182908.csv",
        "../Results/benhui_10s_50ms/benhui_gum_10s_50_ms_actuator_data_20250613-182743.csv",
        "../Results/benhui_10s_60ms/benhui_gum_10s_60_ms_actuator_data_20250613-193131.csv",
        "../Results/benhui_10s_70ms/benhui_gum_10s_70_ms_actuator_data_20250613-182602.csv",
        "../Results/benhui_10s_80ms/benhui_gum_10s_80_ms_actuator_data_20250613-183103.csv",
        "../Results/benhui_10s_90ms/benhui_gum_10s_90_ms_actuator_data_20250613-182359.csv",
        "../Results/benhui_10s_100ms/benhui_gum_10s_100_ms_actuator_data_20250613-182110.csv"
    ]

    time_intervals = [40, 50, 60, 70, 80, 90, 100]
    all_delays = []
    all_rhos = []
    all_rms = []

    for path in actuator_path_names:
        delays, rhos, rms = process_file(path)
        all_delays.append(delays)
        all_rhos.append(rhos)
        all_rms.append(rms)

    delay_dict = {f"Actuator {i}": [d[i] for d in all_delays] for i in range(6)}
    rho_dict = {f"Actuator {i}": [r[i] for r in all_rhos] for i in range(6)}
    rms_dict = {f"Actuator {i}": [rms[i] for rms in all_rms] for i in range(6)}

    plot_results(time_intervals, delay_dict, rho_dict, rms_dict)
