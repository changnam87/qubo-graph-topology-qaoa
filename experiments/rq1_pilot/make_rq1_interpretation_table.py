"""
Create a compact interpretation table for RQ1 pilot results.

Inputs:
    results/rq1_pilot/merged_rq1_metrics.csv
    results/rq1_pilot/rq1_core_correlation_summary.csv

Output:
    results/rq1_pilot/rq1_interpretation_table.csv

This table is intended to support early Results-section writing.
It is not the final statistical model.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_pilot"

MERGED_PATH = RESULTS_DIR / "merged_rq1_metrics.csv"
CORR_PATH = RESULTS_DIR / "rq1_core_correlation_summary.csv"
OUTPUT_PATH = RESULTS_DIR / "rq1_interpretation_table.csv"


def get_corr(corr_df: pd.DataFrame, topology: str, predictor: str, outcome: str):
    """
    Extract one within-topology Spearman correlation.
    """
    row = corr_df[
        (corr_df["scope"] == "within_topology")
        & (corr_df["topology"] == topology)
        & (corr_df["predictor"] == predictor)
        & (corr_df["outcome"] == outcome)
    ]

    if len(row) == 0:
        return None

    return row.iloc[0]["spearman_corr"]


def main() -> None:
    merged = pd.read_csv(MERGED_PATH)
    corr = pd.read_csv(CORR_PATH)

    summary = (
        merged.groupby("topology", as_index=False)
        .agg(
            n_rows=("instance_name", "count"),
            mean_n_edges=("n_edges", "mean"),
            mean_transpiled_depth=("transpiled_depth", "mean"),
            mean_transpiled_2q_count=("transpiled_2q_count", "mean"),
            mean_swap_count=("swap_count", "mean"),
            mean_depth_overhead=("depth_overhead", "mean"),
            mean_twoq_overhead=("twoq_overhead", "mean"),
            mean_transpilation_time_sec=("transpilation_time_sec", "mean"),
        )
    )

    rows = []

    for _, row in summary.iterrows():
        topology = row["topology"]

        rows.append(
            {
                "topology": topology,
                "n_rows": int(row["n_rows"]),

                "mean_n_edges": row["mean_n_edges"],
                "mean_transpiled_depth": row["mean_transpiled_depth"],
                "mean_transpiled_2q_count": row["mean_transpiled_2q_count"],
                "mean_swap_count": row["mean_swap_count"],
                "mean_depth_overhead": row["mean_depth_overhead"],
                "mean_twoq_overhead": row["mean_twoq_overhead"],
                "mean_transpilation_time_sec": row["mean_transpilation_time_sec"],

                "rho_n_edges_pre_depth": get_corr(
                    corr,
                    topology,
                    "n_edges",
                    "pre_transpile_depth",
                ),
                "rho_n_edges_transpiled_depth": get_corr(
                    corr,
                    topology,
                    "n_edges",
                    "transpiled_depth",
                ),
                "rho_n_edges_swap_count": get_corr(
                    corr,
                    topology,
                    "n_edges",
                    "swap_count",
                ),
                "rho_density_transpiled_depth": get_corr(
                    corr,
                    topology,
                    "density",
                    "transpiled_depth",
                ),
                "rho_max_degree_transpiled_depth": get_corr(
                    corr,
                    topology,
                    "max_degree",
                    "transpiled_depth",
                ),
                "rho_weighted_degree_mean_transpiled_depth": get_corr(
                    corr,
                    topology,
                    "weighted_degree_mean",
                    "transpiled_depth",
                ),
            }
        )

    out = pd.DataFrame(rows)

    # More interpretable ordering.
    topology_order = {
        "fully_connected": 0,
        "grid_2d": 1,
        "heavy_hex_like": 2,
        "line": 3,
    }

    out["topology_order"] = out["topology"].map(topology_order)
    out = out.sort_values("topology_order").drop(columns=["topology_order"])

    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ1 interpretation table saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print()
    print(out.to_string(index=False))


if __name__ == "__main__":
    main()
