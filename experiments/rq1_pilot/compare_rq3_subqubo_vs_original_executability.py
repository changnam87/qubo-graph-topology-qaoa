"""
Compare sub-QUBO executability against original-QUBO executability.

Inputs:
    results/rq3_pilot/subqubo_executability_metrics.csv
    results/rq1_extended/transpile_metrics.csv

Output:
    results/rq3_pilot/subqubo_vs_original_executability.csv

Purpose:
    Quantify how much sub-QUBO extraction reduces QAOA circuit/transpilation
    metrics relative to the original QUBO under the same topology.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


RESULTS_DIR = PROJECT_ROOT / "results" / "rq3_pilot"

SUB_EXEC_PATH = RESULTS_DIR / "subqubo_executability_metrics.csv"
ORIGINAL_EXEC_PATH = PROJECT_ROOT / "results" / "rq1_extended" / "transpile_metrics.csv"

OUTPUT_PATH = RESULTS_DIR / "subqubo_vs_original_executability.csv"


def main() -> None:
    sub_df = pd.read_csv(SUB_EXEC_PATH)
    orig_df = pd.read_csv(ORIGINAL_EXEC_PATH)

    # Keep only the same sparse topologies used in RQ3.
    orig_df = orig_df[
        orig_df["topology"].isin(["line", "grid_2d", "heavy_hex_like"])
    ].copy()

    orig_keep = orig_df[
        [
            "instance_name",
            "topology",
            "pre_transpile_depth",
            "pre_transpile_2q_count",
            "transpiled_depth",
            "transpiled_gate_count",
            "transpiled_2q_count",
            "swap_count",
            "depth_overhead",
            "twoq_overhead",
        ]
    ].copy()

    orig_keep = orig_keep.rename(
        columns={
            "instance_name": "original_instance_name",
            "pre_transpile_depth": "original_pre_transpile_depth",
            "pre_transpile_2q_count": "original_pre_transpile_2q_count",
            "transpiled_depth": "original_transpiled_depth",
            "transpiled_gate_count": "original_transpiled_gate_count",
            "transpiled_2q_count": "original_transpiled_2q_count",
            "swap_count": "original_swap_count",
            "depth_overhead": "original_depth_overhead",
            "twoq_overhead": "original_twoq_overhead",
        }
    )

    merged = sub_df.merge(
        orig_keep,
        on=["original_instance_name", "topology"],
        how="left",
        validate="many_to_one",
    )

    # Absolute reductions: positive means sub-QUBO is smaller/cheaper.
    merged["depth_reduction_vs_original"] = (
        merged["original_transpiled_depth"] - merged["transpiled_depth"]
    )

    merged["twoq_reduction_vs_original"] = (
        merged["original_transpiled_2q_count"] - merged["transpiled_2q_count"]
    )

    merged["swap_reduction_vs_original"] = (
        merged["original_swap_count"] - merged["swap_count"]
    )

    merged["pre_depth_reduction_vs_original"] = (
        merged["original_pre_transpile_depth"] - merged["pre_transpile_depth"]
    )

    merged["pre_2q_reduction_vs_original"] = (
        merged["original_pre_transpile_2q_count"] - merged["pre_transpile_2q_count"]
    )

    # Percentage reductions.
    merged["pct_depth_reduction_vs_original"] = (
        100.0
        * merged["depth_reduction_vs_original"]
        / merged["original_transpiled_depth"]
    )

    merged["pct_twoq_reduction_vs_original"] = (
        100.0
        * merged["twoq_reduction_vs_original"]
        / merged["original_transpiled_2q_count"]
    )

    merged["pct_swap_reduction_vs_original"] = merged.apply(
        lambda row: (
            100.0 * row["swap_reduction_vs_original"] / row["original_swap_count"]
            if pd.notna(row["original_swap_count"]) and row["original_swap_count"] != 0
            else None
        ),
        axis=1,
    )

    merged["pct_pre_depth_reduction_vs_original"] = (
        100.0
        * merged["pre_depth_reduction_vs_original"]
        / merged["original_pre_transpile_depth"]
    )

    merged["pct_pre_2q_reduction_vs_original"] = (
        100.0
        * merged["pre_2q_reduction_vs_original"]
        / merged["original_pre_transpile_2q_count"]
    )

    merged.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ3 sub-QUBO vs original executability comparison saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {merged.shape}")
    print()

    print("Missing original metric counts:")
    check_cols = [
        "original_transpiled_depth",
        "original_transpiled_2q_count",
        "original_swap_count",
    ]
    print(merged[check_cols].isna().sum())
    print()

    print("Overall reduction summary by extraction strategy:")
    print(
        merged.groupby("extraction_strategy", as_index=False)
        .agg(
            n_rows=("subqubo_name", "count"),
            mean_weighted_edge_preservation=("weighted_edge_preservation_ratio", "mean"),
            mean_pct_depth_reduction=("pct_depth_reduction_vs_original", "mean"),
            mean_pct_twoq_reduction=("pct_twoq_reduction_vs_original", "mean"),
            mean_pct_swap_reduction=("pct_swap_reduction_vs_original", "mean"),
            mean_depth_reduction=("depth_reduction_vs_original", "mean"),
            mean_twoq_reduction=("twoq_reduction_vs_original", "mean"),
            mean_swap_reduction=("swap_reduction_vs_original", "mean"),
        )
        .round(3)
        .to_string(index=False)
    )

    print()
    print("Preview:")
    print(
        merged[
            [
                "original_family",
                "original_n_variables",
                "k_variables",
                "extraction_strategy",
                "topology",
                "weighted_edge_preservation_ratio",
                "original_transpiled_depth",
                "transpiled_depth",
                "pct_depth_reduction_vs_original",
                "original_swap_count",
                "swap_count",
                "pct_swap_reduction_vs_original",
            ]
        ].head(12).round(3).to_string(index=False)
    )


if __name__ == "__main__":
    main()
