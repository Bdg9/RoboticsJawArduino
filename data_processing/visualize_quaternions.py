#!/usr/bin/env python3
"""
visualize_positions.py
----------------------

Interactive Plotly visualisations of HEAD and JAW *positions*
(exported by OptiTrack / Motive).

* Two separate time-series dashboards:
    1. head_x, head_y, head_z  versus time
    2. jaw_x,  jaw_y,  jaw_z   versus time
* One 3-D path plot (head = blue, jaw = orange).

Usage
-----
    python visualize_positions.py Take*.csv           # live view
    python visualize_positions.py Take*.csv --every 3 # decimate
    python visualize_positions.py Take*.csv \
           --save-prefix pos_vis --no-show            # HTML only
"""

from __future__ import annotations
import argparse
import pathlib
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


# ─────────────────────────── data helpers ────────────────────────────────────
def load_csv(csv_path: pathlib.Path, every: int) -> pd.DataFrame:
    cols = [
        "Frame", "Time",
        "head_px", "head_py", "head_pz",
        "jaw_px",  "jaw_py",  "jaw_pz",
    ]
    df = pd.read_csv(csv_path, skiprows=7, usecols=cols,
                     header=None, names=cols)
    return df.iloc[::every, :].rename(columns={
        "head_px": "head_x", "head_py": "head_y", "head_pz": "head_z",
        "jaw_px":  "jaw_x",  "jaw_py":  "jaw_y",  "jaw_pz":  "jaw_z",
    })


# ────────────────────────── figures ──────────────────────────────────────────
def make_body_ts_fig(df: pd.DataFrame, body: str, colour: str) -> go.Figure:
    """Three stacked sub-plots (x,y,z) for one body."""
    comps = ("x", "y", "z")
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03,
        subplot_titles=[f"{body}_{c}  [mm]" for c in comps],
    )
    for i, c in enumerate(comps, start=1):
        fig.add_trace(
            go.Scatter(
                x=df["Time"],
                y=df[f"{body}_{c}"],
                mode="lines",
                line=dict(width=1.4, color=colour),
                name=f"{body}_{c}",
            ),
            row=i, col=1,
        )
    fig.update_layout(
        height=650,
        title=f"{body.capitalize()} position versus time",
        xaxis3_title="Time [s]",
        showlegend=False,
    )
    return fig


def make_3d_path_fig(df: pd.DataFrame) -> go.Figure:
    colours = dict(head="#1f77b4", jaw="#ff7f0e")
    fig = go.Figure()

    for body, colour in colours.items():
        # path line
        fig.add_trace(go.Scatter3d(
            x=df[f"{body}_x"], y=df[f"{body}_y"], z=df[f"{body}_z"],
            mode="lines", line=dict(width=1, color="rgba(70,70,70,0.35)"),
            showlegend=False, hoverinfo="skip",
        ))
        # points coloured by time
        fig.add_trace(go.Scatter3d(
            x=df[f"{body}_x"], y=df[f"{body}_y"], z=df[f"{body}_z"],
            mode="markers",
            marker=dict(size=4,
                        color=df["Time"],
                        colorscale=("Viridis" if body == "jaw" else "Cividis"),
                        showscale=(body == "jaw"),
                        colorbar=dict(title="Time [s]") if body == "jaw" else None),
            name=f"{body} path",
            customdata=df[["Frame", "Time"]],
            hovertemplate=(
                f"{body}<br>"
                "Frame %{customdata[0]}<br>"
                "t = %{customdata[1]:.3f} s<br>"
                "x = %{x:.1f} mm<br>y = %{y:.1f} mm<br>z = %{z:.1f} mm"
                "<extra></extra>"
            ),
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title="x [mm]",
            yaxis_title="y [mm]",
            zaxis_title="z [mm]",
            aspectmode="data",
        ),
        title="Head (blue) and Jaw (orange) trajectories",
        margin=dict(l=0, r=0, b=0, t=40),
    )
    return fig


# ──────────────────────────── main ───────────────────────────────────────────
def main(csv_file: pathlib.Path, every: int,
         save_prefix: str | None, show: bool) -> None:
    df = load_csv(csv_file, every)

    head_fig = make_body_ts_fig(df, "head", "#1f77b4")
    jaw_fig  = make_body_ts_fig(df, "jaw",  "#ff7f0e")
    path_fig = make_3d_path_fig(df)

    if save_prefix:
        pio.write_html(head_fig, file=f"{save_prefix}_head_time_series.html",
                       auto_open=False)
        pio.write_html(jaw_fig,  file=f"{save_prefix}_jaw_time_series.html",
                       auto_open=False)
        pio.write_html(path_fig, file=f"{save_prefix}_3d_paths.html",
                       auto_open=False)
        print(f"Saved HTML files with prefix '{save_prefix}_...'")

    if show:
        head_fig.show()
        jaw_fig.show()
        path_fig.show()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Interactive head & jaw position plots")
    ap.add_argument("input_csv", type=pathlib.Path,
                    help="Raw Motive CSV export")
    ap.add_argument("--every", type=int, default=1,
                    help="Use every N-th frame (default 1)")
    ap.add_argument("--save-prefix", metavar="NAME",
                    help="Write self-contained HTML files using NAME as prefix")
    ap.add_argument("--no-show", action="store_true",
                    help="Do not open browser windows")
    args = ap.parse_args()
    main(csv_file=args.input_csv,
         every=args.every,
         save_prefix=args.save_prefix,
         show=not args.no_show)
