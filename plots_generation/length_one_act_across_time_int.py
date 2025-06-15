import numpy
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Load the data
actuator_path_names = [#"../Results/benhui_10s_40ms/benhui_gum_10s_40_ms_actuator_data_20250613-182908.csv",
              "../Results/benhui_10s_50ms/benhui_gum_10s_50_ms_actuator_data_20250613-182743.csv",
              "../Results/benhui_10s_60ms/benhui_gum_10s_60_ms_actuator_data_20250613-193131.csv",
              "../Results/benhui_10s_70ms/benhui_gum_10s_70_ms_actuator_data_20250613-182602.csv",
              "../Results/benhui_10s_80ms/benhui_gum_10s_80_ms_actuator_data_20250613-183103.csv",
              "../Results/benhui_10s_90ms/benhui_gum_10s_90_ms_actuator_data_20250613-182359.csv",
              "../Results/benhui_10s_100ms/benhui_gum_10s_100_ms_actuator_data_20250613-182110.csv"]

pose_path_names = [#"../Results/benhui_10s_40ms/benhui_gum_10s_40_ms_pose_data_20250613-182908.csv",
                "../Results/benhui_10s_50ms/benhui_gum_10s_50_ms_pose_data_20250613-182743.csv",
                "../Results/benhui_10s_60ms/benhui_gum_10s_60_ms_pose_data_20250613-193131.csv",
                "../Results/benhui_10s_70ms/benhui_gum_10s_70_ms_pose_data_20250613-182602.csv",
                "../Results/benhui_10s_80ms/benhui_gum_10s_80_ms_pose_data_20250613-183103.csv",
                "../Results/benhui_10s_90ms/benhui_gum_10s_90_ms_pose_data_20250613-182359.csv",
                "../Results/benhui_10s_100ms/benhui_gum_10s_100_ms_pose_data_20250613-182110.csv"]

time_intervals = [ 50, 60, 70, 80, 90, 100]  # in milliseconds
hz = [20, 16.67, 14.29, 12.5, 11.11, 10]  # in Hz

actuator_data = [pd.read_csv(path) for path in actuator_path_names]
pose_data = [pd.read_csv(path) for path in pose_path_names]

# Step 2: extract first none {0, 0, 0, 0, 0, 0} pose time from pose data. Pose data has x,y,z,roll,pitch,yaw,time columns
# crop the actuator data to the first non-zero pose time
def extract_first_non_zero_time(pose_df):
    for index, row in pose_df.iterrows():
        if not all(row[:6] == 0):  # Check if all first six columns are zero
            return row['time']  # Return the time of the first non-zero pose
    return None  # If no non-zero pose is found

def extract_last_non_zero_time(pose_df):
    for index in range(len(pose_df) - 1, -1, -1):
        row = pose_df.iloc[index]
        if not all(row[:6] == 0):  # Check if all first six columns are zero
            return row['time']  # Return the time of the last non-zero pose
    return None  # If no non-zero pose is found

def crop_actuator_data(actuator_df, first_non_zero_time, last_non_zero_time):
    # Crop the actuator data to the first non-zero pose time
    return actuator_df[(actuator_df['time'] >= first_non_zero_time) & (actuator_df['time'] <= last_non_zero_time)]

def extract_actuator(actuator_data, actuator_nb):
    actuator = []
    for df in actuator_data:
        # Append all rows where the actuator column matches the actuator_nb
        actuator.append(df[df['actuator'] == actuator_nb])

# Ste 3: For each actuator, make a plot with 7 subplots, one for each time inteval, with the desired length and current length
# make one figure per actuator

def plot_actuator_1_trajectories(actuator_data, time_intervals):
    """
    Plot desired vs actual actuator length for actuator 1 across different time intervals.
    Creates a figure with 3 columns × 2 rows of subplots.
    """
    fig, axs = plt.subplots(3, 2, figsize=(15, 8), sharex=False, sharey=True)
    axs = axs.flatten()

    for i, (df, interval) in enumerate(zip(actuator_data, time_intervals)):
        # Filter for actuator 1
        df_act1 = df[df['actuator'] == 2]
        #fix time to begin at zero and be in milliseconds
        df_act1['time'] = (df_act1['time'] - df_act1['time'].iloc[0]) / 1000  # Convert to milliseconds

        print(f"Columns in df_act1: {df_act1.columns.tolist()}")

        axs[i].plot(df_act1['time'], df_act1['target_length'], label='Target', linestyle='--')
        axs[i].plot(df_act1['time'], df_act1['current_length'], label='Actual', alpha=0.8)
        axs[i].set_title(f'{interval}ms interval')
        axs[i].set_xlabel("Time (s)")
        axs[i].set_ylabel("Length (mm)")
        axs[i].grid(True)

        if i == 0:
            axs[i].legend()

    plt.tight_layout()
    plt.savefig("actuator_2_trajectories.png", dpi=300)

# crop the actuator data to the first non-zero pose and last non-zero pose time
def crop_all_actuator_data(actuator_data, pose_data):
    cropped_data = []
    for act_df, pose_df in zip(actuator_data, pose_data):
        first_non_zero_time = extract_first_non_zero_time(pose_df)
        last_non_zero_time = extract_last_non_zero_time(pose_df)
        cropped_data.append(crop_actuator_data(act_df, first_non_zero_time, last_non_zero_time))
    return cropped_data

# Step 4: Call the plotting function
cropped_data = crop_all_actuator_data(actuator_data, pose_data)
plot_actuator_1_trajectories(cropped_data, time_intervals)
