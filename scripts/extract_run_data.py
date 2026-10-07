"""Extract the distributions shown on the slides from a local shor-braket checkout.

The hardware results live under ``runs/raw`` of the shor-braket repository, which is not
version controlled. This script copies only what the slides need (ideal, emulator and measured
joint distributions of the count and work registers) into ``data/``, so the figures can be
rebuilt without access to the original run directories.

Task ARNs, account identifiers and bucket names are deliberately not copied.

Usage:
    python scripts/extract_run_data.py --shor-braket-root /path/to/shor-braket
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

WORK_VALUES = 16
ORBIT = [1, 4, 7, 13]

# Run directories under runs/raw, keyed by the number of count qubits.
RUNS = {
    "t2": {
        "hardware": "qpu-garnet-generic-constant-20260923T091415750294Z-369f7a966145",
        "emulation": "n15-emulation-20260923T064512774937Z",
    },
    "t3": {
        "hardware": "qpu-garnet-generic-constant-20260923T103520791869Z-9b99c9f6a27a",
        "emulation": "n15-emulation-20260923T102657882684Z",
    },
}


def _load(path: Path) -> dict[str, Any]:
    """Read one JSON file."""
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def extract_run(raw_root: Path, names: dict[str, str]) -> dict[str, Any]:
    """Collect the distributions and headline metrics of one hardware run.

    Args:
        raw_root: The ``runs/raw`` directory of the shor-braket checkout.
        names: The hardware and emulation run directory names.

    Returns:
        A dictionary holding the joint distributions indexed by ``y * 16 + work``.
    """
    analysis = _load(raw_root / names["hardware"] / "analysis.json")
    emulation = _load(raw_root / names["emulation"] / "result.json")
    config = emulation["configurations"]["garnet/generic-constant"]
    if config["circuit_hash"] != analysis["circuit_hash"]:
        raise ValueError("The emulation and the hardware run used different circuits.")

    shots = analysis["shots"]
    metrics = analysis["metrics"]
    return {
        "count_qubits": emulation["problem"]["count_qubits"],
        "shots": shots,
        "circuit_hash": analysis["circuit_hash"],
        "native_two_qubit_gates": config["gates"]["native_two_qubit"],
        "native_depth": config["gates"]["native_depth"],
        "ideal": analysis["distributions"]["expected"],
        "emulator": config["distributions"]["exact_noisy"],
        "hardware_counts": [round(p * shots) for p in analysis["distributions"]["sampled"]],
        "metrics": {
            "signal_fraction": metrics["signal_fraction_support_mass"],
            "signal_fraction_error": metrics["signal_fraction_support_mass_error"],
            "predicted_signal_fraction": metrics["predicted_signal_fraction"],
            "orbit_mass": metrics["orbit_mass"],
            "low_bit_visibility": metrics["low_bit_visibility"],
            "order_recovery_rate": metrics["order_recovery_rate_sampled"],
            "order_recovery_baseline": metrics["order_recovery_baseline_uniform_y"],
        },
    }


def main() -> None:
    """Write ``data/garnet_2026-09-23.json``."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--shor-braket-root", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data" / "garnet_2026-09-23.json",
    )
    args = parser.parse_args()

    raw_root = args.shor_braket_root / "runs" / "raw"
    payload = {
        "description": (
            "Joint distributions of the count and work registers for the N = 15, a = 7 "
            "order-finding circuit (generic-constant oracle) on IQM Garnet, 2026-09-23. "
            "Index = y * 16 + work. Not a factoring claim."
        ),
        "source": "https://github.com/s-sasaki-earthsea-wizard/shor-braket/wiki/First-Hardware-Run-on-IQM-Garnet",
        "device": "IQM Garnet",
        "work_values": WORK_VALUES,
        "orbit": ORBIT,
        "runs": {key: extract_run(raw_root, names) for key, names in RUNS.items()},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=1)
        handle.write("\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
