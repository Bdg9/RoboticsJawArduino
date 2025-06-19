import pandas as pd
import numpy as np

df = pd.read_csv("../Results/max_x_y_force/trajectory_2_100_ms_force_data_20250619-132749.csv")

# Extract time zero and normalize the time column
#df["time"] = df["time"] / 1000.0  # Convert time from ms to seconds
time_zero = df["time"].iloc[0]
index_times_zeros = df[df["time"] == time_zero].index
if len(index_times_zeros) < 4:
    print(f"Warning: Less than four time zero entries found. Using the second time zero entry as reference.")
    time_zero = df["time"].iloc[1]
    index_times_zeros = df[df["time"] == time_zero].index
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
labels = ["back_right", "front", "back_left", "total"]

for i, df in enumerate(dfs):
    print(f"{labels[i]}: max  x force = {df['Fx'].max()}, max y force = {df['Fy'].max()}")

#do this in a proper way
df_new_total_x = df_front['Fx'].add(df_back_left['Fx'], fill_value=0).sub(df_back_right['Fx'],  fill_value=0)
df_new_total_y = df_front['Fy'].add(df_back_left['Fy'], fill_value=0).sub(df_back_right['Fy'],  fill_value=0)

print(f"new total: max x force = {df_new_total_x.max()}, max y force = {df_new_total_y.max()}")
print(f"min x force = {df_new_total_x.min()}, min y force = {df_new_total_y.min()}")
