"""
Create simple sanity summaries for the RQ1 pilot.

Inputs:
    results/rq1_pilot/merged_rq1_metrics.csv

Outputs:
    results/rq1_pilot/rq1_summary_by_family_topology.csv
    results/rq1_pilot/rq1_correlation_screening.csv

This is not the final statistical analysis.
It is a quick sanity check before formal RQ1 modeling.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_pilot"
MERGED_PATH = RESULTS_DIR / "merged_rq1_metrics.csv"

SUMMARY_PATH = RESULTS_DIR / "rq1_summary_by_family_topology.csv"
CORR_PATH = RESULTS_DIR / "rq1_correlation_screening.csv"


GRAPH_DESCRIPTOR_COLS = [
    "n_edges",
    "density",
    "avg_degree",
    "max_degree",
    "degree_std",
    "weighted_degree_mean",
    "weighted_degree_max",
    "weighted_degree_std",
    "quadratic_coeff_range",
    "coefficient_entropy",
    "coefficient_concentration",
    "connected_components",
    "community_count",
    "modularity",
]

OUTCOME_COLS = [
    "pre_transpile_depth",
    "pre_transpile_gate_count",
    "pre_transpile_2q_count",
    "transpiled_depth",
    "transpiled_gate_count",
    "transpiled_2q_count",
    "swap_count",
    "depth_overhead",
    "twoq_overhead",
    "transpilation_time_sec",
]


def main() -> None:
    df = pd.read_csv(MERGED_PATH)

    # ---------------------------------------------------------------------
    # 1. Family/topology-level summary
    # ---------------------------------------------------------------------
    summary = (
        df.groupby(["family", "topology"], as_index=False)
        .agg(
            n_instances=("instance_name", "count"),
            n_variables_mean=("n_variables", "mean"),
            n_edges_mean=("n_edges", "mean"),
            density_mean=("density", "mean"),
            avg_degree_mean=("avg_degree", "mean"),
            max_degree_mean=("max_degree", "mean"),
            pre_depth_mean=("pre_transpile_depth", "mean"),
            transpiled_depth_mean=("transpiled_depth", "mean"),
            swap_count_mean=("swap_count", "mean"),
            depth_overhead_mean=("depth_overhead", "mean"),
            twoq_overhead_mean=("twoq_overhead", "mean"),
        )
    )

    summary.to_csv(SUMMARY_PATH, index=False)

    # ---------------------------------------------------------------------
    # 2. Simple correlation screening
    # ---------------------------------------------------------------------
    rows = []

    for topology in sorted(df["topology"].unique()):
        sub = df[df["topology"] == topology].copy()

        for graph_col in GRAPH_DESCRIPTOR_COLS:
            for outcome_col in OUTCOME_COLS:
                if graph_col not in sub.columns or outcome_col not in sub.columns:
                    continue

                x = sub[graph_col]
                y = sub[outcome_col]

                if x.nunique(dropna=True) <= 1 or y.nunique(dropna=True) <= 1:
                    corr = None
                else:
                    corr = x.corr(y, method="spearman")

                rows.append(
                    {
                        "topology": topology,
                        "graph_descriptor": graph_col,
                        "outcome_metric": outcome_col,
                        "spearman_corr": corr,
                        "n": len(sub),
                    }
                )

    corr_df = pd.DataFrame(rows)
    corr_df.to_csv(CORR_PATH, index=False)

    print("=" * 80)
    print("RQ1 sanity summaries saved")
    print("=" * 80)
    print(f"summary output: {SUMMARY_PATH}")
    print(f"correlation output: {CORR_PATH}")
    print()

    print("Summary preview:")
    print(summary.head(12).to_string(index=False))
    print()

    print("Top absolute correlations with transpiled_depth:")
    temp = corr_df[corr_df["outcome_metric"] == "transpiled_depth"].copy()
    temp["abs_corr"] = temp["spearman_corr"].abs()
    temp = temp.sort_values("abs_corr", ascending=False)
    print(
        temp[
            [
                "topology",
                "graph_descriptor",
                "outcome_metric",
                "spearman_corr",
                "n",
            ]
        ].head(12).to_string(index=False)
    )


if __name__ == "__main__":
    main()
