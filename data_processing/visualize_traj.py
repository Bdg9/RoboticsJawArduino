#!/usr/bin/env python3
"""
plot_trajectory_3d_interactive.py
---------------------------------

Creates an interactive 3-D plot of the gnathion (jaw) path expressed
in the head reference frame.  Rotate with the mouse to inspect the
trajectory from any angle.

INPUT
-----
A CSV written by `transform_chewing.py`, containing (at least)
    Frame, Time, x_mm, y_mm, z_mm, roll_rad, pitch_rad, yaw_rad

USAGE EXAMPLES
--------------
    # simplest: open a resizable browser window
    python plot_trajectory_3d_interactive.py jaw_in_head_radians.csv

    # decimate heavy recordings (plot every 3rd frame) and save HTML
    python plot_trajectory_3d_interactive.py jaw_in_head_radians.csv \
        --every 3 --save jaw_path.html
"""

from __future__ import annotations
import argparse
import pathlib
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio


def main(csv_file: pathlib.Path, every: int, save_html: str | None) -> None:
    # ── load & (optionally) decimate ────────────────────────────────────────────
    df = pd.read_csv(csv_file)
    df = df.iloc[::every, :]          # keep every-Nth sample if --every > 1

    # ── build Plotly figure ────────────────────────────────────────────────────
    fig = go.Figure(
        data=[
            # thin grey line for overall path
            go.Scatter3d(
                x=df["x_mm"], y=df["y_mm"], z=df["z_mm"],
                mode="lines",
                line=dict(width=1, color="rgba(50,50,50,0.4)"),
                showlegend=False,
                hoverinfo="skip",
            ),
            # coloured points overlayed, shaded by time
            go.Scatter3d(
                x=df["x_mm"], y=df["y_mm"], z=df["z_mm"],
                mode="markers",
                marker=dict(
                    size=4,
                    color=df["Time"],          # colour by time stamp
                    colorscale="Viridis",
                    colorbar=dict(title="Time [s]"),
                ),
                name="Jaw (gnathion)",
                hovertemplate=(
                    "Frame %{customdata[0]}<br>"
                    "t = %{customdata[1]:.3f} s<br>"
                    "x = %{x:.1f} mm<br>"
                    "y = %{y:.1f} mm<br>"
                    "z = %{z:.1f} mm"
                    "<extra></extra>"
                ),
                customdata=df[["Frame", "Time"]],
            ),
        ]
    )

    fig.update_layout(
        title="Jaw trajectory in head frame",
        scene=dict(
            xaxis_title="x [mm]",
            yaxis_title="y [mm]",
            zaxis_title="z [mm]",
            aspectmode="data",   # equal unit lengths
        ),
        margin=dict(l=0, r=0, b=0, t=40),
    )

    # ── display and/or save ────────────────────────────────────────────────────
    if save_html:
        pio.write_html(fig, file=save_html, auto_open=False)
        print(f"Interactive file saved → {save_html}")

    # opens a resizable browser window / notebook cell
    fig.show()


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Interactive 3-D jaw-trajectory plotter")
    p.add_argument("input_csv", type=pathlib.Path, help="CSV with x_mm, y_mm, z_mm")
    p.add_argument(
        "--every",
        type=int,
        default=1,
        help="Plot every N-th frame to lighten dense recordings (default = 1)",
    )
    p.add_argument(
        "--save",
        metavar="FILE.html",
        help="Write an embeddable HTML file (opens with any browser)",
    )
    args = p.parse_args()
    main(args.input_csv, every=args.every, save_html=args.save)
