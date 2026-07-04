from pathlib import Path
import itertools
import numpy as np
import pandas as pd
from scipy.stats import friedmanchisquare, wilcoxon

ROOT = Path(__file__).resolve().parents[1]

in_path = ROOT / "results" / "rq2_full" / "rq2_mapping_metrics.csv"
out_dir = ROOT / "results" / "rq2_full"
out_dir.mkdir(parents=True, exist_ok=True)

if not in_path.exists():
    raise FileNotFoundError(f"Missing input file: {in_path}")

df = pd.read_csv(in_path)

print("Available columns:")
for c in df.columns:
    print(" ", c)

# Expected columns from prior RQ2 figure generation
strategy_col = "strategy_name"
metrics = [
    "transpiled_depth",
    "transpiled_2q_count",
    "swap_count",
]

for c in [strategy_col] + metrics:
    if c not in df.columns:
        raise ValueError(f"Missing required column: {c}")

# Identify block columns: same QUBO/topology condition, different strategies.
# Use all stable identifiers that exist.
candidate_block_cols = [
    "original_instance_name",
    "topology",
]

block_cols = [c for c in candidate_block_cols if c in df.columns]

# Remove columns that may vary by strategy if accidentally included.
block_cols = [c for c in block_cols if c != strategy_col]

if not block_cols:
    raise ValueError(
        "Could not identify block columns. "
        "Need columns such as instance_id/family/n_variables/topology."
    )

print("\nUsing block columns:")
print(block_cols)

strategy_order = [
    "standard_qiskit",
    "natural_fixed",
    "random_fixed",
    "degree_desc_fixed",
    "weighted_degree_desc_fixed",
    "degree_desc_centrality_layout",
    "weighted_degree_desc_centrality_layout",
    "bfs_topology_aware",
]

present_strategies = [s for s in strategy_order if s in df[strategy_col].unique()]
if len(present_strategies) < 2:
    raise ValueError("Need at least two mapping strategies.")

print("\nStrategies:")
print(present_strategies)

def holm_adjust(pvals):
    """
    Holm-Bonferroni adjusted p-values.
    Returns adjusted p-values in the original order.
    """
    pvals = np.asarray(pvals, dtype=float)
    m = len(pvals)
    order = np.argsort(pvals)
    adjusted = np.empty(m, dtype=float)

    running_max = 0.0
    for rank, idx in enumerate(order):
        adj = (m - rank) * pvals[idx]
        running_max = max(running_max, adj)
        adjusted[idx] = min(running_max, 1.0)

    return adjusted

friedman_rows = []
posthoc_rows = []

for metric in metrics:
    # Wide table: one row per matched block, one column per strategy.
    wide = (
        df.pivot_table(
            index=block_cols,
            columns=strategy_col,
            values=metric,
            aggfunc="mean"
        )
        .reset_index()
    )

    available = [s for s in present_strategies if s in wide.columns]
    wide_complete = wide.dropna(subset=available).copy()

    n_blocks = len(wide_complete)
    print(f"\nMetric: {metric}")
    print(f"Complete matched blocks: {n_blocks}")

    if n_blocks < 2:
        raise ValueError(f"Not enough matched blocks for {metric}")

    # Friedman test across all strategies.
    arrays = [wide_complete[s].values for s in available]
    stat, p = friedmanchisquare(*arrays)

    # Mean ranks, lower metric is better.
    ranks = wide_complete[available].rank(axis=1, method="average", ascending=True)
    mean_ranks = ranks.mean(axis=0).to_dict()
    best_rank_strategy = min(mean_ranks, key=mean_ranks.get)

    friedman_rows.append({
        "metric": metric,
        "n_blocks": n_blocks,
        "n_strategies": len(available),
        "friedman_chi2": stat,
        "friedman_p": p,
        "best_mean_rank_strategy": best_rank_strategy,
        "best_mean_rank": mean_ranks[best_rank_strategy],
    })

    # Post-hoc paired Wilcoxon: standard_qiskit vs each other strategy.
    ref = "standard_qiskit"
    if ref not in available:
        raise ValueError("standard_qiskit not found in available strategies.")

    raw_rows = []
    for other in available:
        if other == ref:
            continue

        ref_vals = wide_complete[ref].values
        other_vals = wide_complete[other].values

        # Difference defined as other - standard; positive means standard is lower/better.
        diff = other_vals - ref_vals

        # Wilcoxon on paired values. two-sided is conservative.
        try:
            w_stat, w_p = wilcoxon(other_vals, ref_vals, zero_method="wilcox", alternative="two-sided")
        except ValueError:
            # Happens if all differences are zero.
            w_stat, w_p = np.nan, 1.0

        mean_diff = float(np.mean(diff))
        median_diff = float(np.median(diff))
        win_rate = float(np.mean(ref_vals < other_vals))
        tie_rate = float(np.mean(ref_vals == other_vals))
        loss_rate = float(np.mean(ref_vals > other_vals))

        raw_rows.append({
            "metric": metric,
            "comparison": f"{ref} vs {other}",
            "reference": ref,
            "other_strategy": other,
            "n_blocks": n_blocks,
            "wilcoxon_stat": w_stat,
            "p_raw": w_p,
            "mean_other_minus_standard": mean_diff,
            "median_other_minus_standard": median_diff,
            "standard_win_rate": win_rate,
            "tie_rate": tie_rate,
            "standard_loss_rate": loss_rate,
        })

    adj = holm_adjust([r["p_raw"] for r in raw_rows])
    for r, p_adj in zip(raw_rows, adj):
        r["p_holm"] = p_adj
        r["significant_holm_0.05"] = bool(p_adj < 0.05)
        posthoc_rows.append(r)

friedman_df = pd.DataFrame(friedman_rows)
posthoc_df = pd.DataFrame(posthoc_rows)

friedman_path = out_dir / "table_rq2_friedman_tests.csv"
posthoc_path = out_dir / "table_rq2_holm_posthoc_vs_standard_qiskit.csv"

friedman_df.to_csv(friedman_path, index=False)
posthoc_df.to_csv(posthoc_path, index=False)

summary_path = out_dir / "rq2_statistical_validation_summary.md"

with open(summary_path, "w") as f:
    f.write("# RQ2 statistical validation summary\n\n")
    f.write("## Friedman tests\n\n")
    f.write(friedman_df.to_string(index=False))
    f.write("\n\n## Holm-corrected post-hoc tests vs standard Qiskit\n\n")
    f.write(posthoc_df.to_string(index=False))
    f.write("\n")

print("\nSaved:")
print(friedman_path)
print(posthoc_path)
print(summary_path)

print("\nFriedman tests:")
print(friedman_df)

print("\nPost-hoc tests vs standard Qiskit:")
print(posthoc_df)
