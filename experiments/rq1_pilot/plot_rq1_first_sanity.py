"""
Create the first sanity visualization for RQ1 pilot.

Plot:
    n_edges vs transpiled_depth

Input:
    results/rq1_pilot/merged_rq1_metrics.csv

Output:
    results/rq1_pilot/fig_n_edges_vs_transpiled_depth.png

This is not a final paper figure yet.
It is a quick visual check that QUBO graph complexity and transpiled
QAOA circuit complexity move together.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_pilot"
MERGED_PATH = RESULTS_DIR / "merged_rq1_metrics.csv"
FIG_PATH = RESULTS_DIR / "fig_n_edges_vs_transpiled_depth.png"


def main() -> None:
    df = pd.read_csv(MERGED_PATH)

    fig, ax = plt.subplots(figsize=(7.0, 5.0))

    markers = {
        "line": "o",
        "grid_2d": "s",
        "heavy_hex_like": "^",
        "fully_connected": "D",
    }

    for topology, sub in df.groupby("topology"):
        ax.scatter(
            sub["n_edges"],
            sub["transpiled_depth"],
            label=topology,
            marker=markers.get(topology, "o"),
            alpha=0.75,
        )

    ax.set_xlabel("Number of QUBO interaction edges")
    ax.set_ylabel("Transpiled QAOA circuit depth")
    ax.set_title("RQ1 pilot: QUBO graph edges vs transpiled circuit depth")
    ax.legend(title="Topology")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(FIG_PATH, dpi=300)

    print("=" * 80)
    print("RQ1 first sanity plot saved")
    print("=" * 80)
    print(f"output: {FIG_PATH}")
    print()
    print("Data summary:")
    print(
        df.groupby("topology")
        .agg(
            n_rows=("instance_name", "count"),
            n_edges_mean=("n_edges", "mean"),
            transpiled_depth_mean=("transpiled_depth", "mean"),
            swap_count_mean=("swap_count", "mean"),
        )
        .reset_index()
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
