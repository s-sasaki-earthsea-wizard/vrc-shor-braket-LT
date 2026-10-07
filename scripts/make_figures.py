"""Draw the hardware-result figures used on the slides.

Reads ``data/garnet_2026-09-23.json`` (written by ``extract_run_data.py``) and writes SVG files
to ``slides-jp/assets/images/``. The model predictions that are not part of the run data are
the values published on the shor-braket Wiki page "First-Hardware-Run-on-IQM-Garnet".

Colour carries identity and stays fixed across every figure: blue is the ideal distribution,
orange is the hardware, aqua is a model prediction.

Usage:
    python scripts/make_figures.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.figure import Figure
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "garnet_2026-09-23.json"
OUTPUT_DIR = ROOT / "slides-jp" / "assets" / "images"

SURFACE = "#fcfcfb"
TEXT_PRIMARY = "#0b0b0b"
TEXT_SECONDARY = "#52514e"
GRID = "#e6e5e1"
MUTED = "#c3c2b7"

IDEAL = "#2a78d6"
HARDWARE = "#eb6834"
MODEL = "#1baf7a"

# One hue, light to dark. The first stop is the surface so that zero recedes.
SEQUENTIAL = LinearSegmentedColormap.from_list(
    "sequential_blue",
    [SURFACE, "#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"],
)

# Wiki "First-Hardware-Run-on-IQM-Garnet" section 5 (t = 2, signal fraction lambda).
LAMBDA_MODELS_T2 = [
    ("Emulator (calibration noise)", 0.564),
    ("+ asymmetric readout", 0.565),
    ("+ idle T1/T2 (Ramsey T2)", 0.291),
    ("+ idle T1/T2 (echo T2)", 0.292),
]

# Wiki section 7 (t = 3, low-bit visibility, predictions registered before the run).
VISIBILITY_EMULATOR_T3 = 0.83
VISIBILITY_IDLE_MODEL_T3 = (0.25, 0.42)
VISIBILITY_ERROR_T3 = 0.018
PASS_LINE = 0.5


def configure_style() -> None:
    """Set the shared look: quiet axes, slide-sized text."""
    plt.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "font.size": 15,
            "text.color": TEXT_PRIMARY,
            "axes.labelcolor": TEXT_SECONDARY,
            "axes.edgecolor": GRID,
            "axes.titlesize": 16,
            "axes.titleweight": "bold",
            "axes.titlelocation": "left",
            "xtick.color": TEXT_SECONDARY,
            "ytick.color": TEXT_SECONDARY,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "legend.frameon": False,
            "svg.fonttype": "path",
        }
    )


def save(figure: Figure, stem: str) -> None:
    """Write one figure as SVG."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    figure.savefig(OUTPUT_DIR / f"{stem}.svg", bbox_inches="tight")
    plt.close(figure)


def joint_matrix(flat: list[float], work_values: int) -> np.ndarray:
    """Reshape a flat joint distribution into rows of y and columns of work."""
    return np.asarray(flat, dtype=float).reshape(-1, work_values)


def hardware_frequencies(run: dict[str, Any]) -> list[float]:
    """Turn the measured counts into relative frequencies."""
    return [count / run["shots"] for count in run["hardware_counts"]]


def draw_heatmap(ax: Axes, matrix: np.ndarray, vmax: float, orbit: list[int]) -> Any:
    """Draw one joint distribution with a surface-coloured gap between the cells."""
    mesh = ax.pcolormesh(
        matrix, cmap=SEQUENTIAL, vmin=0.0, vmax=vmax, edgecolors=SURFACE, linewidth=2
    )
    rows, columns = matrix.shape
    ax.invert_yaxis()
    ax.set_yticks(np.arange(rows) + 0.5, [str(y) for y in range(rows)])
    ax.set_xticks(np.arange(columns) + 0.5, [str(w) for w in range(columns)])
    for label, value in zip(ax.get_xticklabels(), range(columns)):
        if value in orbit:
            label.set_fontweight("bold")
            label.set_color(TEXT_PRIMARY)
    ax.tick_params(length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return mesh


def plot_joint_t2(data: dict[str, Any]) -> None:
    """Ideal, emulator and hardware joint distributions for t = 2."""
    run = data["runs"]["t2"]
    metrics = run["metrics"]
    panels = [
        ("Ideal: 16 equal cells on the orbit {1, 4, 7, 13}", run["ideal"]),
        (
            f"Emulator prediction (signal fraction {metrics['predicted_signal_fraction']:.2f})",
            run["emulator"],
        ),
        (
            f"IQM Garnet, {run['shots']} shots (signal fraction {metrics['signal_fraction']:.2f})",
            hardware_frequencies(run),
        ),
    ]
    vmax = max(run["ideal"])
    figure, axes = plt.subplots(3, 1, figsize=(12, 7.4), sharex=True)
    mesh = None
    for ax, (title, flat) in zip(axes, panels):
        mesh = draw_heatmap(ax, joint_matrix(flat, data["work_values"]), vmax, data["orbit"])
        ax.set_title(title)
        ax.set_ylabel("count y")
    axes[-1].set_xlabel("work register value")
    figure.subplots_adjust(hspace=0.42, right=0.9)
    colorbar_axis = figure.add_axes((0.92, 0.2, 0.015, 0.6))
    colorbar = figure.colorbar(mesh, cax=colorbar_axis)
    colorbar.set_label("probability")
    colorbar.outline.set_visible(False)
    save(figure, "garnet_t2_joint")


def plot_ideal_t2(data: dict[str, Any]) -> None:
    """The ideal joint distribution for t = 2 alone, shown before the hardware result."""
    run = data["runs"]["t2"]
    figure, ax = plt.subplots(figsize=(12, 2.6))
    draw_heatmap(
        ax, joint_matrix(run["ideal"], data["work_values"]), max(run["ideal"]), data["orbit"]
    )
    ax.set_title("Ideal: 16 equal cells on the orbit {1, 4, 7, 13}")
    ax.set_ylabel("count y")
    ax.set_xlabel("work register value")
    save(figure, "garnet_t2_ideal")


def plot_stripes_t2(data: dict[str, Any]) -> None:
    """The ideal stripes above what the hardware returned, for t = 2."""
    run = data["runs"]["t2"]
    vmax = max(run["ideal"])
    figure, axes = plt.subplots(2, 1, figsize=(10, 4.6), sharex=True)
    for ax, (title, flat) in zip(
        axes, [("ideal", run["ideal"]), ("IQM Garnet", hardware_frequencies(run))]
    ):
        draw_heatmap(ax, joint_matrix(flat, data["work_values"]), vmax, data["orbit"])
        ax.set_yticks([])
        ax.set_ylabel(title, rotation=0, ha="right", va="center", color=TEXT_PRIMARY)
    axes[-1].set_xlabel("work register value")
    figure.subplots_adjust(hspace=0.12)
    save(figure, "garnet_t2_stripes")


def plot_work_marginal_t2(data: dict[str, Any]) -> None:
    """Work register marginal for t = 2: the four most frequent values are the orbit."""
    run = data["runs"]["t2"]
    orbit = data["orbit"]
    marginal = joint_matrix(hardware_frequencies(run), data["work_values"]).sum(axis=0)
    values = np.arange(data["work_values"])
    colors = [HARDWARE if value in orbit else MUTED for value in values]

    figure, ax = plt.subplots(figsize=(11, 5.2))
    ax.bar(values, marginal, width=0.62, color=colors, zorder=3)
    for value in orbit:
        ax.hlines(0.25, value - 0.36, value + 0.36, color=IDEAL, linewidth=2, zorder=4)
        ax.text(
            value,
            marginal[value] + 0.006,
            f"{marginal[value]:.3f}",
            ha="center",
            va="bottom",
            fontsize=13,
        )
    ax.axhline(1 / 16, color=TEXT_SECONDARY, linewidth=1, linestyle=(0, (4, 3)), zorder=2)
    ax.text(10.5, 1 / 16 + 0.004, "uniform noise 1/16", ha="center", va="bottom", fontsize=12,
            color=TEXT_SECONDARY)
    ax.set_xticks(values, [f"{value}\n{value:04b}" for value in values], fontsize=12)
    ax.set_xlabel("work register value (decimal / binary)")
    ax.set_ylabel("probability")
    ax.set_ylim(0, 0.285)
    ax.yaxis.grid(True, color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.set_title("Work register on IQM Garnet (t = 2, 3000 shots)")
    ax.legend(
        handles=[
            Patch(color=IDEAL, label="ideal"),
            Patch(color=HARDWARE, label="hardware, on the orbit"),
            Patch(color=MUTED, label="hardware, off the orbit"),
        ],
        loc="upper left",
        bbox_to_anchor=(0.53, 0.84),
        fontsize=12,
    )
    save(figure, "garnet_t2_work_marginal")


def plot_lambda_models_t2(data: dict[str, Any]) -> None:
    """Signal fraction at t = 2: emulator variants against the hardware."""
    metrics = data["runs"]["t2"]["metrics"]
    labels = [label for label, _ in LAMBDA_MODELS_T2] + ["IQM Garnet (3000 shots)"]
    values = [value for _, value in LAMBDA_MODELS_T2] + [metrics["signal_fraction"]]
    colors = [MODEL] * len(LAMBDA_MODELS_T2) + [HARDWARE]
    positions = np.arange(len(labels))[::-1]

    figure, ax = plt.subplots(figsize=(11, 4.6))
    ax.barh(positions, values, height=0.5, color=colors, zorder=3)
    ax.errorbar(
        values[-1],
        positions[-1],
        xerr=metrics["signal_fraction_error"],
        color=TEXT_PRIMARY,
        capsize=4,
        linewidth=1.5,
        zorder=4,
    )
    for position, value in zip(positions, values):
        ax.text(value + 0.022, position, f"{value:.3f}", va="center", fontsize=14)
    ax.axvline(PASS_LINE, color=TEXT_SECONDARY, linewidth=1, linestyle=(0, (4, 3)), zorder=2)
    ax.text(PASS_LINE + 0.008, len(labels) - 0.42, "gate threshold 0.5", fontsize=12,
            color=TEXT_SECONDARY, va="bottom")
    ax.set_yticks(positions, labels)
    ax.set_xlim(0, 0.75)
    ax.set_ylim(-0.6, len(labels) - 0.1)
    ax.set_xlabel("signal fraction (1 = ideal distribution, 0 = uniform noise)")
    ax.xaxis.grid(True, color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)
    ax.legend(
        handles=[Patch(color=MODEL, label="model prediction"), Patch(color=HARDWARE, label="hardware")],
        loc="lower right",
        fontsize=12,
    )
    save(figure, "garnet_t2_lambda_models")


def plot_y_marginal_t3(data: dict[str, Any]) -> None:
    """Count register marginal for t = 3: odd values appear only when the idle qubit dephases."""
    run = data["runs"]["t3"]
    series = [
        ("ideal", IDEAL, joint_matrix(run["ideal"], data["work_values"]).sum(axis=1)),
        ("emulator prediction", MODEL, joint_matrix(run["emulator"], data["work_values"]).sum(axis=1)),
        (
            "IQM Garnet (3000 shots)",
            HARDWARE,
            joint_matrix(hardware_frequencies(run), data["work_values"]).sum(axis=1),
        ),
    ]
    values = np.arange(len(series[0][2]))
    width = 0.24

    figure, ax = plt.subplots(figsize=(11, 5.0))
    for index, (label, color, marginal) in enumerate(series):
        ax.bar(values + (index - 1) * (width + 0.02), marginal, width=width, color=color,
               label=label, zorder=3)
    ax.axhline(1 / 8, color=TEXT_SECONDARY, linewidth=1, linestyle=(0, (4, 3)), zorder=2)
    ax.text(7.55, 1 / 8 + 0.005, "fully\ndephased\n1/8", ha="left", va="bottom", fontsize=12,
            color=TEXT_SECONDARY)
    ax.set_xlim(-0.6, 8.5)
    ax.set_xticks(values, [f"{value}\n{value:03b}" for value in values])
    ax.set_xlabel("count register value y (decimal / binary); only even y is allowed")
    ax.set_ylabel("probability")
    ax.set_ylim(0, 0.3)
    ax.yaxis.grid(True, color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.set_title("Count register on IQM Garnet (t = 3)")
    ax.legend(loc="upper right", ncols=3, fontsize=12, bbox_to_anchor=(1.0, 1.0))
    save(figure, "garnet_t3_y_marginal")


def plot_visibility_t3(data: dict[str, Any]) -> None:
    """Low-bit visibility at t = 3: both predictions against the hardware."""
    visibility = data["runs"]["t3"]["metrics"]["low_bit_visibility"]
    low, high = VISIBILITY_IDLE_MODEL_T3
    labels = ["Emulator (calibration noise)", "+ idle T1/T2 (pre-registered)", "IQM Garnet (3000 shots)"]
    positions = np.arange(len(labels))[::-1]

    figure, ax = plt.subplots(figsize=(11, 3.6))
    ax.barh(positions[0], VISIBILITY_EMULATOR_T3, height=0.5, color=MODEL, zorder=3)
    ax.barh(positions[1], high - low, left=low, height=0.5, color=MODEL, zorder=3)
    ax.barh(positions[2], visibility, height=0.5, color=HARDWARE, zorder=3)
    ax.errorbar(visibility, positions[2], xerr=VISIBILITY_ERROR_T3, color=TEXT_PRIMARY,
                capsize=4, linewidth=1.5, zorder=4)
    ax.text(VISIBILITY_EMULATOR_T3 + 0.02, positions[0], f"{VISIBILITY_EMULATOR_T3:.2f}",
            va="center", fontsize=14)
    ax.text(high + 0.02, positions[1], f"{low:.2f} to {high:.2f}", va="center", fontsize=14)
    ax.text(visibility + 0.04, positions[2], f"{visibility:.3f} ± {VISIBILITY_ERROR_T3:.3f}",
            va="center", fontsize=14)
    ax.set_yticks(positions, labels)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.6, len(labels) - 0.4)
    ax.set_xlabel("low-bit visibility (1 = phase kept, 0 = fully dephased)")
    ax.xaxis.grid(True, color=GRID, linewidth=1, zorder=0)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.spines["left"].set_visible(False)
    ax.legend(
        handles=[Patch(color=MODEL, label="model prediction"), Patch(color=HARDWARE, label="hardware")],
        loc="lower right",
        fontsize=12,
    )
    save(figure, "garnet_t3_visibility")


def main() -> None:
    """Draw every figure."""
    with DATA_PATH.open(encoding="utf-8") as handle:
        data = json.load(handle)
    configure_style()
    plot_ideal_t2(data)
    plot_stripes_t2(data)
    plot_joint_t2(data)
    plot_work_marginal_t2(data)
    plot_lambda_models_t2(data)
    plot_y_marginal_t3(data)
    plot_visibility_t3(data)
    print(f"Wrote figures to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
