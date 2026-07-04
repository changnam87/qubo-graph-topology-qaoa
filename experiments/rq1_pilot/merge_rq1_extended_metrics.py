"""
Merge graph descriptors and transpilation metrics for the extended RQ1 dataset.

Inputs:
    results/rq1_extended/graph_metrics.csv
    results/rq1_extended/transpile_metrics.csv

Output:
    results/rq1_extended/merged_rq1_metrics.csv

This merged file is the main analysis-ready dataset for extended RQ1.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_extended"

GRAPH_METRICS_PATH = RESULTS_DIR / "graph_metrics.csv"
TRANSPILE_METRICS_PATH = RESULTS_DIR / "transpile_metrics.csv"
OUTPUT_PATH = RESULTS_DIR / "merged_rq1_metrics.csv"


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)
    transpile_df = pd.read_csv(TRANSPILE_METRICS_PATH)

    # These columns already exist in transpile_df or are metadata that should not duplicate.
    graph_columns_to_drop = [
        "family",
        "n_variables",
        "constant",
        "seed",
        "qubo_json",
        "edge_probability",
        "n_items",
        "n_bins",
        "n_operations",
        "n_machines",
        "conflict_probability",
        "n_conflict_pairs",
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

    # Derived analysis variables
    merged["edge_to_variable_ratio"] = merged["n_edges"] / merged["n_variables"]

    merged["swap_per_qubo_edge"] = (
        merged["swap_count"] / merged["n_edges"].replace(0, pd.NA)
    )

    merged["transpiled_2q_per_qubo_edge"] = (
        merged["transpiled_2q_count"] / merged["n_edges"].replace(0, pd.NA)
    )

    merged["depth_per_qubo_edge"] = (
        merged["transpiled_depth"] / merged["n_edges"].replace(0, pd.NA)
    )

    merged["gate_count_overhead"] = (
        merged["transpiled_gate_count"] / merged["pre_transpile_gate_count"]
    )

    merged.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("Extended merged RQ1 metrics saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {merged.shape}")
    print()
    print("family counts:")
    print(merged["family"].value_counts())
    print()
    print("topology counts:")
    print(merged["topology"].value_counts())
    print()
    print("variable-size counts:")
    print(merged["n_variables"].value_counts().sort_index())
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
