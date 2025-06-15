import pandas as pd
import matplotlib.pyplot as plt

def plot_force_distrib(file_path, line_coords):
    # Load the CSV file
    df = pd.read_csv(file_path)

    # Extract time zero and normalize the time column
    #df["time"] = df["time"] / 1000.0  # Convert time from ms to seconds
    time_zero = df["time"].iloc[0]
    index_times_zeros = df[df["time"] == time_zero].index
    if len(index_times_zeros) < 4:
        raise ValueError("The CSV file does not contain enough time zero entries to split the data into four parts.")
    if len(index_times_zeros) > 4:
        print(f"Warning: More than four time zero entries found. Deleting indices that are too close together.")
        #delete indexes too close to each other
        for i in range(len(index_times_zeros) - 1, 0, -1):
            if index_times_zeros[i] - index_times_zeros[i-1] < 10:
                index_times_zeros = index_times_zeros.drop(index_times_zeros[i])
    if len(index_times_zeros) != 4:
        raise ValueError(f"Expected exactly four time zero entries, found {len(index_times_zeros)}. Please check the data.")
    df_front = df.iloc[index_times_zeros[0]:index_times_zeros[1]]
    df_back_right = df.iloc[index_times_zeros[1]:index_times_zeros[2]]
    df_back_left = df.iloc[index_times_zeros[2]:index_times_zeros[3]]
    df_total = df.iloc[index_times_zeros[3]:]

    dfs = [df_back_right, df_front, df_back_left, df_total]
    #for all dataframes, convert time to seconds
    for df in dfs:
        df["time"] = (df["time"] - time_zero) / 1000.0  # Convert time from ms to seconds

    #find crop indices
    df_total_sup_20N = df_total[df_total["Fz"] > 20.0]
    if not df_total_sup_20N.empty:
        start_time = df_total_sup_20N["time"].iloc[0] - 4
        end_time = df_total_sup_20N["time"].iloc[-1] + 3

    dfs_cropped = []
    for df in dfs:
        df_cropped = df[(df["time"] >= start_time) & (df["time"] <= end_time)]
        #reset time to start at zero
        df_cropped["time"] = df_cropped["time"] - df_cropped["time"].iloc[0]
        dfs_cropped.append(df_cropped) 
    
    labels = ["Back Right (N)", "Front (N)", "Back Left (N)", "Total (N)"]

    # Plotting
    plt.figure(figsize=(10, 8))
    for i, df in enumerate(dfs_cropped):
        plt.subplot(4, 1, i + 1)
        plt.plot(df["time"], df["Fz"], label=labels[i])
        plt.ylabel(labels[i])
        plt.grid()
        if i == 3:
            plt.xlabel("Time (s)")
        else:
            plt.tick_params(labelbottom=False)  # Hide x-axis labels for all but the last subplot

    # draw 2 red vertical lines at 13s and 29s over all subplots
    plt.axvline(x=line_coords[0], color='red', linestyle='--', label='13s')
    plt.axvline(x=line_coords[1], color='red', linestyle='--', label='29s')


    plt.tight_layout()
    plt_name = file_path.split("/")[-2].replace(".csv", ".png")
    plt.savefig(plt_name, dpi=300)
    plt.close()


file_paths = [
            "../Results/ForceDistribution/Force_distrib_test_2000_ms_force_data_20250613-134941.csv",
            "../Results/ForceDistribution_tpu/Force_distrib_test_2000_ms_force_data_20250613-184539.csv",
            "../Results/ForceDistribution2/Force_distrib_test_2000_ms_force_data_20250613-142821.csv",
            "../Results/ForceDistributionGum/Force_distrib_test_2500_ms_force_data_20250613-143514.csv"
            ]

line_coords = [
    [13, 25],  # Coordinates for the first line
    [14.5, 26.5],  # Coordinates for the second line
    [13, 25],  # Coordinates for the third line
    [13, 29]   # Coordinates for the fourth line
]
for i, file_path in enumerate(file_paths):
    print(f"Processing file: {file_path}")
    plot_force_distrib(file_path, line_coords[i])
    print(f"Plot saved for {file_path}\n")

            