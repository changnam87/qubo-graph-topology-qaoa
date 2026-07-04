"""
Create summary tables for full RQ2 mapping experiment.

Input:
    results/rq2_full/rq2_mapping_metrics.csv

Outputs:
    results/rq2_full/table_rq2_strategy_summary.csv
    results/rq2_full/table_rq2_family_strategy_summary.csv
    results/rq2_full/table_rq2_topology_strategy_summary.csv
    results/rq2_full/table_rq2_win_rates.csv

Purpose:
    Summarize RQ2 results for manuscript Results-section drafting.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


RESULTS_DIR = PROJECT_ROOT / "results" / "rq2_full"
INPUT_PATH = RESULTS_DIR / "rq2_mapping_metrics.csv"

STRATEGY_SUMMARY_PATH = RESULTS_DIR / "table_rq2_strategy_summary.csv"
FAMILY_STRATEGY_PATH = RESULTS_DIR / "table_rq2_family_strategy_summary.csv"
TOPOLOGY_STRATEGY_PATH = RESULTS_DIR / "table_rq2_topology_strategy_summary.csv"
WIN_RATE_PATH = RESULTS_DIR / "table_rq2_win_rates.csv"


def summarize(grouped):
    """
    Common aggregation for RQ2 strategy summaries.
    """
    return grouped.agg(
        n_rows=("original_instance_name", "count"),

        mean_depth=("transpiled_depth", "mean"),
        mean_2q=("transpiled_2q_count", "mean"),
        mean_swap=("swap_count", "mean"),

        mean_depth_overhead=("depth_overhead", "mean"),
        mean_twoq_overhead=("twoq_overhead", "mean"),

        mean_delta_depth_vs_natural_fixed=("delta_depth_vs_natural_fixed", "mean"),
        mean_delta_2q_vs_natural_fixed=("delta_2q_vs_natural_fixed", "mean"),
        mean_delta_swap_vs_natural_fixed=("delta_swap_vs_natural_fixed", "mean"),

        mean_pct_depth_vs_natural_fixed=("pct_depth_change_vs_natural_fixed", "mean"),
        mean_pct_2q_vs_natural_fixed=("pct_2q_change_vs_natural_fixed", "mean"),
        mean_pct_swap_vs_natural_fixed=("pct_swap_change_vs_natural_fixed", "mean"),

        mean_delta_depth_vs_standard_qiskit=("delta_depth_vs_standard_qiskit", "mean"),
        mean_delta_2q_vs_standard_qiskit=("delta_2q_vs_standard_qiskit", "mean"),
        mean_delta_swap_vs_standard_qiskit=("delta_swap_vs_standard_qiskit", "mean"),

        mean_transpilation_time_sec=("transpilation_time_sec", "mean"),
    ).reset_index()


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    # ------------------------------------------------------------------
    # 1. Overall strategy summary
    # ------------------------------------------------------------------
    strategy_summary = summarize(
        df.groupby("strategy_name", as_index=False)
    )

    strategy_summary.to_csv(STRATEGY_SUMMARY_PATH, index=False)

    # ------------------------------------------------------------------
    # 2. Family x strategy summary
    # ------------------------------------------------------------------
    family_strategy = summarize(
        df.groupby(["family", "strategy_name"], as_index=False)
    )

    family_strategy.to_csv(FAMILY_STRATEGY_PATH, index=False)

    # ------------------------------------------------------------------
    # 3. Topology x strategy summary
    # ------------------------------------------------------------------
    topology_strategy = summarize(
        df.groupby(["topology", "strategy_name"], as_index=False)
    )

    topology_strategy.to_csv(TOPOLOGY_STRATEGY_PATH, index=False)

    # ------------------------------------------------------------------
    # 4. Win rates vs natural_fixed and standard_qiskit
    # ------------------------------------------------------------------
    win_df = df.copy()

    win_df["depth_win_vs_natural_fixed"] = (
        win_df["delta_depth_vs_natural_fixed"] < 0
    )
    win_df["twoq_win_vs_natural_fixed"] = (
        win_df["delta_2q_vs_natural_fixed"] < 0
    )
    win_df["swap_win_vs_natural_fixed"] = (
        win_df["delta_swap_vs_natural_fixed"] < 0
    )

    win_df["depth_win_vs_standard_qiskit"] = (
        win_df["delta_depth_vs_standard_qiskit"] < 0
    )
    win_df["twoq_win_vs_standard_qiskit"] = (
        win_df["delta_2q_vs_standard_qiskit"] < 0
    )
    win_df["swap_win_vs_standard_qiskit"] = (
        win_df["delta_swap_vs_standard_qiskit"] < 0
    )

    win_rates = (
        win_df.groupby("strategy_name", as_index=False)
        .agg(
            n_rows=("original_instance_name", "count"),

            depth_win_rate_vs_natural_fixed=("depth_win_vs_natural_fixed", "mean"),
            twoq_win_rate_vs_natural_fixed=("twoq_win_vs_natural_fixed", "mean"),
            swap_win_rate_vs_natural_fixed=("swap_win_vs_natural_fixed", "mean"),

            depth_win_rate_vs_standard_qiskit=("depth_win_vs_standard_qiskit", "mean"),
            twoq_win_rate_vs_standard_qiskit=("twoq_win_vs_standard_qiskit", "mean"),
            swap_win_rate_vs_standard_qiskit=("swap_win_vs_standard_qiskit", "mean"),
        )
    )

    win_rates.to_csv(WIN_RATE_PATH, index=False)

    print("=" * 80)
    print("RQ2 summary tables saved")
    print("=" * 80)
    print(f"strategy summary: {STRATEGY_SUMMARY_PATH}")
    print(f"family x strategy summary: {FAMILY_STRATEGY_PATH}")
    print(f"topology x strategy summary: {TOPOLOGY_STRATEGY_PATH}")
    print(f"win rates: {WIN_RATE_PATH}")
    print()

    print("Strategy summary preview:")
    print(
        strategy_summary[
            [
                "strategy_name",
                "n_rows",
                "mean_delta_depth_vs_natural_fixed",
                "mean_delta_2q_vs_natural_fixed",
                "mean_delta_swap_vs_natural_fixed",
                "mean_pct_depth_vs_natural_fixed",
                "mean_pct_2q_vs_natural_fixed",
                "mean_pct_swap_vs_natural_fixed",
                "mean_delta_depth_vs_standard_qiskit",
                "mean_delta_2q_vs_standard_qiskit",
                "mean_delta_swap_vs_standard_qiskit",
            ]
        ].round(3).to_string(index=False)
    )

    print()
    print("Win rate preview:")
    print(
        win_rates[
            [
                "strategy_name",
                "n_rows",
                "depth_win_rate_vs_natural_fixed",
                "twoq_win_rate_vs_natural_fixed",
                "swap_win_rate_vs_natural_fixed",
                "depth_win_rate_vs_standard_qiskit",
                "twoq_win_rate_vs_standard_qiskit",
                "swap_win_rate_vs_standard_qiskit",
            ]
        ].round(3).to_string(index=False)
    )


if __name__ == "__main__":
    main()
