"""
Create final RQ3 pilot trade-off table.

Inputs:
    results/rq3_pilot/subqubo_vs_original_executability.csv
    results/rq3_pilot/subqubo_solution_quality_metrics.csv

Output:
    results/rq3_pilot/rq3_final_tradeoff_table.csv

This table combines:
    1. interaction preservation
    2. executability improvement vs original QUBO
    3. solution-quality preservation gap
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


RESULTS_DIR = PROJECT_ROOT / "results" / "rq3_pilot"

EXEC_PATH = RESULTS_DIR / "subqubo_vs_original_executability.csv"
QUALITY_PATH = RESULTS_DIR / "subqubo_solution_quality_metrics.csv"

OUTPUT_PATH = RESULTS_DIR / "rq3_final_tradeoff_table.csv"


def main() -> None:
    exec_df = pd.read_csv(EXEC_PATH)
    quality_df = pd.read_csv(QUALITY_PATH)

    # Quality metrics are per sub-QUBO.
    # Executability metrics are per sub-QUBO x topology.
    # Summarize executability first to sub-QUBO level.
    exec_summary = (
        exec_df.groupby(
            [
                "original_instance_name",
                "subqubo_name",
                "original_family",
                "original_n_variables",
                "k_variables",
                "extraction_strategy",
            ],
            as_index=False,
        )
        .agg(
            mean_weighted_edge_preservation=("weighted_edge_preservation_ratio", "mean"),
            mean_edge_preservation=("edge_preservation_ratio", "mean"),

            mean_pct_depth_reduction_vs_original=("pct_depth_reduction_vs_original", "mean"),
            mean_pct_twoq_reduction_vs_original=("pct_twoq_reduction_vs_original", "mean"),
            mean_pct_swap_reduction_vs_original=("pct_swap_reduction_vs_original", "mean"),

            mean_depth_reduction_vs_original=("depth_reduction_vs_original", "mean"),
            mean_twoq_reduction_vs_original=("twoq_reduction_vs_original", "mean"),
            mean_swap_reduction_vs_original=("swap_reduction_vs_original", "mean"),

            mean_sub_transpiled_depth=("transpiled_depth", "mean"),
            mean_sub_transpiled_2q=("transpiled_2q_count", "mean"),
            mean_sub_swap_count=("swap_count", "mean"),

            mean_original_transpiled_depth=("original_transpiled_depth", "mean"),
            mean_original_transpiled_2q=("original_transpiled_2q_count", "mean"),
            mean_original_swap_count=("original_swap_count", "mean"),
        )
    )

    quality_keep = quality_df[
        [
            "original_instance_name",
            "subqubo_name",
            "original_family",
            "original_n_variables",
            "k_variables",
            "extraction_strategy",

            "original_reference_energy",
            "subqubo_exact_energy",
            "lifted_original_energy",
            "energy_gap_vs_reference",
            "normalized_energy_gap_vs_reference",
            "lifted_hamming_weight",
            "original_reference_hamming_weight",
        ]
    ].copy()

    merged = exec_summary.merge(
        quality_keep,
        on=[
            "original_instance_name",
            "subqubo_name",
            "original_family",
            "original_n_variables",
            "k_variables",
            "extraction_strategy",
        ],
        how="left",
        validate="one_to_one",
    )

    # Summary table by family, k, and strategy.
    final = (
        merged.groupby(
            [
                "original_family",
                "k_variables",
                "extraction_strategy",
            ],
            as_index=False,
        )
        .agg(
            n_subqubos=("subqubo_name", "count"),

            mean_weighted_edge_preservation=("mean_weighted_edge_preservation", "mean"),
            mean_edge_preservation=("mean_edge_preservation", "mean"),

            mean_pct_depth_reduction_vs_original=("mean_pct_depth_reduction_vs_original", "mean"),
            mean_pct_twoq_reduction_vs_original=("mean_pct_twoq_reduction_vs_original", "mean"),
            mean_pct_swap_reduction_vs_original=("mean_pct_swap_reduction_vs_original", "mean"),

            mean_sub_transpiled_depth=("mean_sub_transpiled_depth", "mean"),
            mean_sub_transpiled_2q=("mean_sub_transpiled_2q", "mean"),
            mean_sub_swap_count=("mean_sub_swap_count", "mean"),

            mean_energy_gap_vs_reference=("energy_gap_vs_reference", "mean"),
            median_energy_gap_vs_reference=("energy_gap_vs_reference", "median"),
            mean_normalized_energy_gap_vs_reference=("normalized_energy_gap_vs_reference", "mean"),
            median_normalized_energy_gap_vs_reference=("normalized_energy_gap_vs_reference", "median"),

            mean_lifted_hamming_weight=("lifted_hamming_weight", "mean"),
            mean_original_reference_hamming_weight=("original_reference_hamming_weight", "mean"),
        )
    )

    # Preservation-executability-quality efficiency proxies.
    # Higher is better for preservation per cost; lower is better for gap.
    final["weighted_preservation_per_depth"] = (
        final["mean_weighted_edge_preservation"] / final["mean_sub_transpiled_depth"]
    )

    final["weighted_preservation_per_swap_plus_one"] = (
        final["mean_weighted_edge_preservation"] / (final["mean_sub_swap_count"] + 1.0)
    )

    final["quality_gap_per_weighted_preservation"] = (
        final["mean_normalized_energy_gap_vs_reference"]
        / (final["mean_weighted_edge_preservation"] + 1e-9)
    )

    final.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ3 final trade-off table saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {final.shape}")
    print()

    print("Overall by extraction strategy:")
    overall = (
        final.groupby("extraction_strategy", as_index=False)
        .agg(
            n_rows=("n_subqubos", "sum"),
            mean_weighted_edge_preservation=("mean_weighted_edge_preservation", "mean"),
            mean_pct_depth_reduction=("mean_pct_depth_reduction_vs_original", "mean"),
            mean_pct_twoq_reduction=("mean_pct_twoq_reduction_vs_original", "mean"),
            mean_pct_swap_reduction=("mean_pct_swap_reduction_vs_original", "mean"),
            mean_normalized_gap=("mean_normalized_energy_gap_vs_reference", "mean"),
            mean_preservation_per_depth=("weighted_preservation_per_depth", "mean"),
            mean_gap_per_preservation=("quality_gap_per_weighted_preservation", "mean"),
        )
        .round(4)
    )
    print(overall.to_string(index=False))

    print()
    print("Preview:")
    print(
        final[
            [
                "original_family",
                "k_variables",
                "extraction_strategy",
                "mean_weighted_edge_preservation",
                "mean_pct_depth_reduction_vs_original",
                "mean_pct_twoq_reduction_vs_original",
                "mean_pct_swap_reduction_vs_original",
                "mean_normalized_energy_gap_vs_reference",
                "weighted_preservation_per_depth",
                "quality_gap_per_weighted_preservation",
            ]
        ].round(4).head(24).to_string(index=False)
    )


if __name__ == "__main__":
    main()
