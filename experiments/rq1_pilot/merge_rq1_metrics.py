"""
Merge graph descriptors and transpilation metrics for RQ1 analysis.

Inputs:
    results/rq1_pilot/graph_metrics.csv
    results/rq1_pilot/transpile_metrics.csv

Output:
    results/rq1_pilot/merged_rq1_metrics.csv

This merged file is the main analysis-ready dataset for RQ1.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_pilot"

GRAPH_METRICS_PATH = RESULTS_DIR / "graph_metrics.csv"
TRANSPILE_METRICS_PATH = RESULTS_DIR / "transpile_metrics.csv"
OUTPUT_PATH = RESULTS_DIR / "merged_rq1_metrics.csv"


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)
    transpile_df = pd.read_csv(TRANSPILE_METRICS_PATH)

    # Avoid duplicate columns after merging.
    graph_columns_to_drop = [
        "family",
        "n_variables",
        "constant",
        "seed",
        "qubo_json",
        "edge_probability",
        "n_items",
        "n_bins",
    ]

    graph_features = graph_df.drop(
        columns=[col for col in graph_columns_to_drop if col in graph_df.columns]
    )

    merged = transpile_df.merge(
        graph_features,
        on="instance_name",
        how="left",
        validate="many_to_one",
    )

    # Simple sanity-derived metrics useful for later RQ1 analysis.
    merged["edge_to_variable_ratio"] = merged["n_edges"] / merged["n_variables"]

    merged["swap_per_qubo_edge"] = merged["swap_count"] / merged["n_edges"].replace(0, pd.NA)

    merged["transpiled_2q_per_qubo_edge"] = (
        merged["transpiled_2q_count"] / merged["n_edges"].replace(0, pd.NA)
    )

    merged["depth_per_qubo_edge"] = (
        merged["transpiled_depth"] / merged["n_edges"].replace(0, pd.NA)
    )

    merged.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("Merged RQ1 metrics saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {merged.shape}")
    print()
    print("topology counts:")
    print(merged["topology"].value_counts())
    print()
    print("family counts:")
    print(merged["family"].value_counts())
    print()
    print("missing values in key graph columns:")
    key_cols = [
        "n_edges",
        "density",
        "avg_degree",
        "max_degree",
        "weighted_degree_mean",
        "coefficient_entropy",
        "community_count",
        "modularity",
    ]
    print(merged[key_cols].isna().sum())
    print()
    print("preview:")
    print(
        merged[
            [
                "instance_name",
                "family",
                "n_variables",
                "topology",
                "n_edges",
                "density",
                "avg_degree",
                "max_degree",
                "pre_transpile_depth",
                "transpiled_depth",
                "swap_count",
                "depth_overhead",
                "twoq_overhead",
            ]
        ].head(12).to_string(index=False)
    )


if __name__ == "__main__":
    main()
