"""
Summarize RQ3 preservation-executability trade-offs.

Input:
    results/rq3_pilot/subqubo_executability_metrics.csv

Output:
    results/rq3_pilot/rq3_tradeoff_summary.csv

This summary combines:
    - interaction preservation
    - weighted interaction preservation
    - QAOA/transpilation executability metrics
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


RESULTS_DIR = PROJECT_ROOT / "results" / "rq3_pilot"

INPUT_PATH = RESULTS_DIR / "subqubo_executability_metrics.csv"
OUTPUT_PATH = RESULTS_DIR / "rq3_tradeoff_summary.csv"


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    summary = (
        df.groupby(["original_family", "k_variables", "extraction_strategy"], as_index=False)
        .agg(
            n_rows=("subqubo_name", "count"),

            mean_variable_preservation=("variable_preservation_ratio", "mean"),
            mean_edge_preservation=("edge_preservation_ratio", "mean"),
            mean_weighted_edge_preservation=("weighted_edge_preservation_ratio", "mean"),

            mean_pre_depth=("pre_transpile_depth", "mean"),
            mean_pre_2q=("pre_transpile_2q_count", "mean"),

            mean_transpiled_depth=("transpiled_depth", "mean"),
            mean_transpiled_2q=("transpiled_2q_count", "mean"),
            mean_swap_count=("swap_count", "mean"),

            mean_depth_overhead=("depth_overhead", "mean"),
            mean_twoq_overhead=("twoq_overhead", "mean"),
            mean_transpilation_time_sec=("transpilation_time_sec", "mean"),
        )
    )

    # Simple efficiency ratios:
    # Higher preservation per transpilation cost is better.
    summary["weighted_preservation_per_depth"] = (
        summary["mean_weighted_edge_preservation"] / summary["mean_transpiled_depth"]
    )

    summary["weighted_preservation_per_2q"] = (
        summary["mean_weighted_edge_preservation"] / summary["mean_transpiled_2q"]
    )

    summary["weighted_preservation_per_swap_plus_one"] = (
        summary["mean_weighted_edge_preservation"] / (summary["mean_swap_count"] + 1.0)
    )

    summary.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ3 preservation-executability trade-off summary saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {summary.shape}")
    print()

    print("Overall by extraction strategy:")
    overall = (
        df.groupby("extraction_strategy", as_index=False)
        .agg(
            n_rows=("subqubo_name", "count"),
            mean_edge_preservation=("edge_preservation_ratio", "mean"),
            mean_weighted_edge_preservation=("weighted_edge_preservation_ratio", "mean"),
            mean_transpiled_depth=("transpiled_depth", "mean"),
            mean_transpiled_2q=("transpiled_2q_count", "mean"),
            mean_swap_count=("swap_count", "mean"),
            mean_depth_overhead=("depth_overhead", "mean"),
            mean_twoq_overhead=("twoq_overhead", "mean"),
        )
    )

    print(overall.round(3).to_string(index=False))

    print()
    print("Trade-off summary preview:")
    print(
        summary[
            [
                "original_family",
                "k_variables",
                "extraction_strategy",
                "mean_weighted_edge_preservation",
                "mean_transpiled_depth",
                "mean_transpiled_2q",
                "mean_swap_count",
                "weighted_preservation_per_depth",
                "weighted_preservation_per_swap_plus_one",
            ]
        ].round(4).head(24).to_string(index=False)
    )


if __name__ == "__main__":
    main()
