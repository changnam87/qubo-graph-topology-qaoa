"""
Core correlation check for RQ1 pilot.

This script extracts a small set of interpretable Spearman correlations
from merged_rq1_metrics.csv.

This is still a pilot-level sanity check, not final statistical modeling.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_pilot"
MERGED_PATH = RESULTS_DIR / "merged_rq1_metrics.csv"
OUTPUT_PATH = RESULTS_DIR / "rq1_core_correlation_summary.csv"


PREDICTORS = [
    "n_edges",
    "density",
    "avg_degree",
    "max_degree",
    "weighted_degree_mean",
    "weighted_degree_max",
    "coefficient_entropy",
    "modularity",
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


def spearman_corr(x, y):
    """
    Compute Spearman correlation safely.
    """
    if x.nunique(dropna=True) <= 1:
        return None

    if y.nunique(dropna=True) <= 1:
        return None

    return x.corr(y, method="spearman")


def main() -> None:
    df = pd.read_csv(MERGED_PATH)

    rows = []

    # Overall correlations across all topologies
    for predictor in PREDICTORS:
        for outcome in OUTCOMES:
            rows.append(
                {
                    "scope": "all_topologies",
                    "topology": "all",
                    "predictor": predictor,
                    "outcome": outcome,
                    "spearman_corr": spearman_corr(df[predictor], df[outcome]),
                    "n": len(df),
                }
            )

    # Topology-specific correlations
    for topology, sub in df.groupby("topology"):
        for predictor in PREDICTORS:
            for outcome in OUTCOMES:
                rows.append(
                    {
                        "scope": "within_topology",
                        "topology": topology,
                        "predictor": predictor,
                        "outcome": outcome,
                        "spearman_corr": spearman_corr(sub[predictor], sub[outcome]),
                        "n": len(sub),
                    }
                )

    out = pd.DataFrame(rows)
    out["abs_spearman_corr"] = out["spearman_corr"].abs()

    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ1 core correlation summary saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {out.shape}")
    print()

    print("Core correlations for n_edges:")
    core = out[
        (out["predictor"] == "n_edges")
        & (out["outcome"].isin(["pre_transpile_depth", "transpiled_depth", "swap_count"]))
    ].copy()

    print(
        core[
            [
                "scope",
                "topology",
                "predictor",
                "outcome",
                "spearman_corr",
                "n",
            ]
        ].to_string(index=False)
    )

    print()
    print("Top correlations with transpiled_depth:")
    top = out[out["outcome"] == "transpiled_depth"].copy()
    top = top.sort_values("abs_spearman_corr", ascending=False)

    print(
        top[
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
