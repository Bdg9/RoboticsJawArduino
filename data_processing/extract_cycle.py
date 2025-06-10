from __future__ import annotations
import argparse
import pandas as pd
import pathlib
import numpy as np

def main(input_csv: pathlib.Path, output_csv: pathlib.Path) -> None:
    """Extract chewing cycles from filtered CSV data."""
    df = pd.read_csv(input_csv)
    
    # Ensure the DataFrame has the necessary columns
    if not {"Frame", "Time", "x_mm", "y_mm", "z_mm"}.issubset(df.columns):
        raise ValueError("Input CSV must contain Frame, Time, x_mm, y_mm, z_mm columns")

    # take 59s to 85s of the recording
    start_time = 59.0
    end_time = 85.0
    df = df[(df["Time"] >= start_time) & (df["Time"] <= end_time)].reset_index(drop=True)
    if df.empty:
        raise ValueError("No data in the specified time range")
    
    #print data range
    print("Data range:")
    for col in ["x_mm", "y_mm", "z_mm", "roll_rad", "pitch_rad", "yaw_rad"]:
        if col in df.columns:
            print(f"  {col}: {df[col].min():.2f} to {df[col].max():.2f}")
        else:
            print(f"  {col}: not found in input CSV")
    if df.empty:
        print("No data to process, exiting.")
        return
    
    #save to output CSV without frame and time columns
    df = df[["x_mm", "y_mm", "z_mm", "roll_rad", "pitch_rad", "yaw_rad"]]
    df.to_csv(output_csv, index=False)


# ────────────────────────────────── CLI ───────────────────────────────────────
if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Cycle extractor for chewing data")
    ap.add_argument("input_csv",  type=pathlib.Path, help="Filtered CSV")
    ap.add_argument("output_csv", type=pathlib.Path, help="Destination CSV")
    args = ap.parse_args()
    main(args.input_csv, args.output_csv)