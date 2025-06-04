#!/usr/bin/env python3
"""
plot_trajectory_3d_interactive.py
---------------------------------

• 3-D interactive plot of the gnathion (jaw) path in the head frame.
• 6-DoF time-series dashboard (x, y, z, roll, pitch, yaw).

INPUT
-----
CSV from `transform_chewing.py` with columns
  Frame, Time, x_mm, y_mm, z_mm, roll_rad, pitch_rad, yaw_rad

EXAMPLES
--------
  # live view in your browser
  python plot_trajectory_3d_interactive.py jaw_in_head_radians.csv

  # decimate heavy recordings, write HTML files only
  python plot_trajectory_3d_interactive.py jaw_in_head_radians.csv \
      --every 3 --save-prefix jaw_vis --no-show
"""

from __future__ import annotations
import argparse
import pathlib
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


# ───────────────────────────── helpers ────────────────────────────────────────
def make_3d_fig(df: pd.DataFrame) -> go.Figure:
    """Rotatable 3-D path, coloured by Time."""
    return go.Figure(
        data=[
            go.Scatter3d(
                x=df["x_mm"], y=df["y_mm"], z=df["z_mm"],
                mode="lines",
                line=dict(width=1, color="rgba(50,50,50,0.4)"),
                showlegend=False, hoverinfo="skip",
            ),
            go.Scatter3d(
                x=df["x_mm"], y=df["y_mm"], z=df["z_mm"],
                mode="markers",
                marker=dict(
                    size=4, color=df["Time"],
                    colorscale="Viridis",
                    colorbar=dict(title="Time [s]"),
                ),
                name="Jaw (gnathion)",
                customdata=df[["Frame", "Time"]],
                hovertemplate=(
                    "Frame %{customdata[0]}<br>"
                    "t = %{customdata[1]:.3f} s<br>"
                    "x = %{x:.1f} mm<br>"
                    "y = %{y:.1f} mm<br>"
                    "z = %{z:.1f} mm"
                    "<extra></extra>"
                ),
            ),
        ],
        layout=dict(
            title="Jaw trajectory in head frame",
            scene=dict(
                xaxis_title="x [mm]",
                yaxis_title="y [mm]",
                zaxis_title="z [mm]",
                aspectmode="data",
            ),
            margin=dict(l=0, r=0, b=0, t=40),
        ),
    )


def make_ts_fig(df: pd.DataFrame) -> go.Figure:
    """Six stacked sub-plots: x, y, z, roll, pitch, yaw."""
    comps = [
        ("x_mm", "x [mm]"),
        ("y_mm", "y [mm]"),
        ("z_mm", "z [mm]"),
        ("roll_rad",  "roll [rad]"),
        ("pitch_rad", "pitch [rad]"),
        ("yaw_rad",   "yaw [rad]"),
    ]
    fig = make_subplots(
        rows=6, cols=1, shared_xaxes=True,
        vertical_spacing=0.02,
        subplot_titles=[label for _, label in comps],
    )

    for i, (col, label) in enumerate(comps, start=1):
        fig.add_trace(
            go.Scatter(
                x=df["Time"], y=df[col],
                mode="lines", line=dict(width=1.3, color="#1f77b4"),
                name=label,
            ),
            row=i, col=1,
        )

    fig.update_layout(
        height=1000,
        title="Jaw 6-DoF versus time (head frame)",
        showlegend=False,
        xaxis6_title="Time [s]",
        margin=dict(t=50),
    )
    return fig


# ───────────────────────────── main ───────────────────────────────────────────
def main(
    csv_file: pathlib.Path, every: int,
    save_prefix: str | None, show: bool,
) -> None:
    df = pd.read_csv(csv_file).iloc[::every, :]          # optional decimation

    #print min and max of each column
    print("Data range:")
    for col in df.columns:
        if col in ["Frame", "Time"]:
            continue
        print(f"  {col}: {df[col].min():.2f} to {df[col].max():.2f}")
    print(f"Loaded {len(df)} rows from {csv_file}")
    if df.empty:
        print("No data to plot, exiting.")
        return

    fig_3d = make_3d_fig(df)
    fig_ts = make_ts_fig(df)

    if save_prefix:
        pio.write_html(fig_3d, file=f"{save_prefix}_3d.html",      auto_open=False)
        pio.write_html(fig_ts, file=f"{save_prefix}_time_series.html", auto_open=False)
        print(f"Saved → {save_prefix}_3d.html  &  {save_prefix}_time_series.html")

    if show:
        fig_3d.show()
        fig_ts.show()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="3-D and 6-DoF jaw visualisation")
    ap.add_argument("input_csv", type=pathlib.Path,
                    help="CSV with x_mm, y_mm, z_mm, roll_rad, pitch_rad, yaw_rad")
    ap.add_argument("--every", type=int, default=1,
                    help="Plot every N-th frame (default 1 = all)")
    ap.add_argument("--save-prefix", metavar="NAME",
                    help="Write HTML files using NAME as prefix")
    ap.add_argument("--no-show", action="store_true",
                    help="Suppress live browser windows")
    args = ap.parse_args()
    main(
        csv_file=args.input_csv,
        every=args.every,
        save_prefix=args.save_prefix,
        show=not args.no_show,
    )
