"""
Create final RQ1 figures for the extended analysis.

Input:
    results/rq1_extended/merged_rq1_metrics_with_alignment.csv

Outputs:
    results/rq1_extended/fig_rq1a_edges_vs_transpiled_depth.png
    results/rq1_extended/fig_rq1b_topology_distance_vs_swap_count.png

Figure RQ1-A:
    QUBO interaction edges vs transpiled QAOA circuit depth.

Figure RQ1-B:
    Weighted mean topology distance vs SWAP count.

These figures are intended as near-paper-ready RQ1 figures.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import matplotlib.pyplot as plt


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_extended"
INPUT_PATH = RESULTS_DIR / "merged_rq1_metrics_with_alignment.csv"

FIG_A_PATH = RESULTS_DIR / "fig_rq1a_edges_vs_transpiled_depth.png"
FIG_B_PATH = RESULTS_DIR / "fig_rq1b_topology_distance_vs_swap_count.png"


TOPOLOGY_MARKERS = {
    "fully_connected": "D",
    "grid_2d": "s",
    "heavy_hex_like": "^",
    "line": "o",
}


def plot_edges_vs_transpiled_depth(df: pd.DataFrame) -> None:
    """
    Figure RQ1-A:
    n_edges vs transpiled_depth, grouped by topology.
    """
    fig, ax = plt.subplots(figsize=(7.2, 5.2))

    for topology, sub in df.groupby("topology"):
        ax.scatter(
            sub["n_edges"],
            sub["transpiled_depth"],
            label=topology,
            marker=TOPOLOGY_MARKERS.get(topology, "o"),
            alpha=0.72,
            s=42,
        )

    ax.set_xlabel("Number of QUBO interaction edges")
    ax.set_ylabel("Transpiled QAOA circuit depth")
    ax.set_title("RQ1-A: QUBO graph size and transpiled circuit depth")
    ax.grid(True, alpha=0.25)
    ax.legend(title="Topology", frameon=True)

    fig.tight_layout()
    fig.savefig(FIG_A_PATH, dpi=300)
    plt.close(fig)


def plot_topology_distance_vs_swap_count(df: pd.DataFrame) -> None:
    """
    Figure RQ1-B:
    weighted_mean_topology_distance vs swap_count, grouped by topology.

    Fully connected topology is included, but it appears at distance = 1
    and swap_count = 0 because every QUBO edge is directly aligned.
    """
    fig, ax = plt.subplots(figsize=(7.2, 5.2))

    for topology, sub in df.groupby("topology"):
        ax.scatter(
            sub["weighted_mean_topology_distance"],
            sub["swap_count"],
            label=topology,
            marker=TOPOLOGY_MARKERS.get(topology, "o"),
            alpha=0.72,
            s=42,
        )

    ax.set_xlabel("Weighted mean topology distance")
    ax.set_ylabel("SWAP count")
    ax.set_title("RQ1-B: QUBO-topology distance and SWAP overhead")
    ax.grid(True, alpha=0.25)
    ax.legend(title="Topology", frameon=True)

    fig.tight_layout()
    fig.savefig(FIG_B_PATH, dpi=300)
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    plot_edges_vs_transpiled_depth(df)
    plot_topology_distance_vs_swap_count(df)

    print("=" * 80)
    print("RQ1 final figures saved")
    print("=" * 80)
    print(f"Figure RQ1-A: {FIG_A_PATH}")
    print(f"Figure RQ1-B: {FIG_B_PATH}")
    print()

    print("Figure data summary:")
    print(
        df.groupby("topology", as_index=False)
        .agg(
            n_rows=("instance_name", "count"),
            n_edges_mean=("n_edges", "mean"),
            transpiled_depth_mean=("transpiled_depth", "mean"),
            weighted_distance_mean=("weighted_mean_topology_distance", "mean"),
            swap_count_mean=("swap_count", "mean"),
        )
        .round(3)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
