"""
Create final RQ1 summary tables for the extended dataset.

Input:
    results/rq1_extended/merged_rq1_metrics_with_alignment.csv

Outputs:
    results/rq1_extended/table_rq1_family_topology_summary.csv
    results/rq1_extended/table_rq1_key_correlations.csv

These tables are intended for Results-section drafting.
They are descriptive and correlational, not causal.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_extended"

INPUT_PATH = RESULTS_DIR / "merged_rq1_metrics_with_alignment.csv"
SUMMARY_TABLE_PATH = RESULTS_DIR / "table_rq1_family_topology_summary.csv"
CORR_TABLE_PATH = RESULTS_DIR / "table_rq1_key_correlations.csv"


GRAPH_PREDICTORS = [
    "n_edges",
    "density",
    "avg_degree",
    "max_degree",
    "weighted_degree_mean",
    "weighted_degree_max",
    "coefficient_entropy",
    "modularity",
]

ALIGNMENT_PREDICTORS = [
    "topology_alignment_ratio",
    "weighted_topology_alignment_ratio",
    "mean_topology_distance",
    "weighted_mean_topology_distance",
    "max_topology_distance",
]

OUTCOMES = [
    "pre_transpile_depth",
    "pre_transpile_2q_count",
    "transpiled_depth",
    "transpiled_2q_count",
    "swap_count",
    "depth_overhead",
    "twoq_overhead",
]


def safe_spearman(x, y):
    """
    Compute Spearman correlation safely.
    """
    if x.nunique(dropna=True) <= 1:
        return None

    if y.nunique(dropna=True) <= 1:
        return None

    return x.corr(y, method="spearman")


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    # ------------------------------------------------------------------
    # Table 1: family x topology summary
    # ------------------------------------------------------------------
    summary = (
        df.groupby(["family", "topology"], as_index=False)
        .agg(
            n_rows=("instance_name", "count"),
            n_variables_mean=("n_variables", "mean"),
            n_edges_mean=("n_edges", "mean"),
            density_mean=("density", "mean"),
            topology_alignment_mean=("topology_alignment_ratio", "mean"),
            mean_topology_distance_mean=("mean_topology_distance", "mean"),
            pre_depth_mean=("pre_transpile_depth", "mean"),
            transpiled_depth_mean=("transpiled_depth", "mean"),
            transpiled_2q_count_mean=("transpiled_2q_count", "mean"),
            swap_count_mean=("swap_count", "mean"),
            depth_overhead_mean=("depth_overhead", "mean"),
            twoq_overhead_mean=("twoq_overhead", "mean"),
            transpilation_time_mean=("transpilation_time_sec", "mean"),
        )
    )

    summary.to_csv(SUMMARY_TABLE_PATH, index=False)

    # ------------------------------------------------------------------
    # Table 2: key correlations
    # ------------------------------------------------------------------
    predictors = GRAPH_PREDICTORS + ALIGNMENT_PREDICTORS

    rows = []

    # Overall correlations
    for predictor in predictors:
        for outcome in OUTCOMES:
            rows.append(
                {
                    "scope": "all_topologies",
                    "topology": "all",
                    "predictor_type": (
                        "alignment" if predictor in ALIGNMENT_PREDICTORS else "graph"
                    ),
                    "predictor": predictor,
                    "outcome": outcome,
                    "spearman_rho": safe_spearman(df[predictor], df[outcome]),
                    "n": len(df),
                }
            )

    # Within-topology correlations
    for topology, sub in df.groupby("topology"):
        for predictor in predictors:
            for outcome in OUTCOMES:
                rows.append(
                    {
                        "scope": "within_topology",
                        "topology": topology,
                        "predictor_type": (
                            "alignment" if predictor in ALIGNMENT_PREDICTORS else "graph"
                        ),
                        "predictor": predictor,
                        "outcome": outcome,
                        "spearman_rho": safe_spearman(sub[predictor], sub[outcome]),
                        "n": len(sub),
                    }
                )

    corr = pd.DataFrame(rows)
    corr["abs_spearman_rho"] = corr["spearman_rho"].abs()
    corr.to_csv(CORR_TABLE_PATH, index=False)

    print("=" * 80)
    print("RQ1 final summary tables saved")
    print("=" * 80)
    print(f"summary table: {SUMMARY_TABLE_PATH}")
    print(f"correlation table: {CORR_TABLE_PATH}")
    print()

    print("Table 1 preview:")
    print(
        summary[
            [
                "family",
                "topology",
                "n_rows",
                "n_edges_mean",
                "topology_alignment_mean",
                "mean_topology_distance_mean",
                "transpiled_depth_mean",
                "swap_count_mean",
                "depth_overhead_mean",
                "twoq_overhead_mean",
            ]
        ].head(16).round(3).to_string(index=False)
    )

    print()
    print("Key correlations with transpiled_depth:")
    temp = corr[
        (corr["outcome"] == "transpiled_depth")
        & (
            corr["predictor"].isin(
                [
                    "n_edges",
                    "density",
                    "max_degree",
                    "weighted_degree_mean",
                    "topology_alignment_ratio",
                    "mean_topology_distance",
                    "weighted_mean_topology_distance",
                ]
            )
        )
    ].copy()

    print(
        temp[
            [
                "scope",
                "topology",
                "predictor_type",
                "predictor",
                "outcome",
                "spearman_rho",
                "n",
            ]
        ].round(3).to_string(index=False)
    )

    print()
    print("Key correlations with swap_count:")
    temp2 = corr[
        (corr["outcome"] == "swap_count")
        & (
            corr["predictor"].isin(
                [
                    "n_edges",
                    "density",
                    "max_degree",
                    "weighted_degree_mean",
                    "topology_alignment_ratio",
                    "mean_topology_distance",
                    "weighted_mean_topology_distance",
                ]
            )
        )
    ].copy()

    print(
        temp2[
            [
                "scope",
                "topology",
                "predictor_type",
                "predictor",
                "outcome",
                "spearman_rho",
                "n",
            ]
        ].round(3).to_string(index=False)
    )


if __name__ == "__main__":
    main()
