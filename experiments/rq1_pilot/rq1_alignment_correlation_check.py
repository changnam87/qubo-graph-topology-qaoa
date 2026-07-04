"""
Correlation screening for topology-alignment descriptors in RQ1 extended dataset.

Input:
    results/rq1_extended/merged_rq1_metrics_with_alignment.csv

Output:
    results/rq1_extended/rq1_alignment_correlation_summary.csv

This is a sanity check before formal RQ1 modeling.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_extended"

INPUT_PATH = RESULTS_DIR / "merged_rq1_metrics_with_alignment.csv"
OUTPUT_PATH = RESULTS_DIR / "rq1_alignment_correlation_summary.csv"


ALIGNMENT_PREDICTORS = [
    "topology_alignment_ratio",
    "weighted_topology_alignment_ratio",
    "mean_topology_distance",
    "weighted_mean_topology_distance",
    "max_topology_distance",
]

OVERHEAD_OUTCOMES = [
    "swap_count",
    "depth_overhead",
    "twoq_overhead",
    "transpiled_depth",
    "transpiled_2q_count",
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

    rows = []

    # Overall across all topologies
    for predictor in ALIGNMENT_PREDICTORS:
        for outcome in OVERHEAD_OUTCOMES:
            rows.append(
                {
                    "scope": "all_topologies",
                    "topology": "all",
                    "predictor": predictor,
                    "outcome": outcome,
                    "spearman_corr": safe_spearman(df[predictor], df[outcome]),
                    "n": len(df),
                }
            )

    # Within each topology
    for topology, sub in df.groupby("topology"):
        for predictor in ALIGNMENT_PREDICTORS:
            for outcome in OVERHEAD_OUTCOMES:
                rows.append(
                    {
                        "scope": "within_topology",
                        "topology": topology,
                        "predictor": predictor,
                        "outcome": outcome,
                        "spearman_corr": safe_spearman(sub[predictor], sub[outcome]),
                        "n": len(sub),
                    }
                )

    out = pd.DataFrame(rows)
    out["abs_spearman_corr"] = out["spearman_corr"].abs()

    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ1 alignment correlation summary saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {out.shape}")
    print()

    print("Overall alignment correlations with overhead:")
    overall = out[
        (out["scope"] == "all_topologies")
        & (out["outcome"].isin(["swap_count", "depth_overhead", "twoq_overhead"]))
    ].copy()
    print(
        overall[
            [
                "predictor",
                "outcome",
                "spearman_corr",
                "n",
            ]
        ].to_string(index=False)
    )

    print()
    print("Top absolute correlations with swap_count:")
    top_swap = out[out["outcome"] == "swap_count"].copy()
    top_swap = top_swap.sort_values("abs_spearman_corr", ascending=False)

    print(
        top_swap[
            [
                "scope",
                "topology",
                "predictor",
                "outcome",
                "spearman_corr",
                "n",
            ]
        ].head(15).to_string(index=False)
    )


if __name__ == "__main__":
    main()
