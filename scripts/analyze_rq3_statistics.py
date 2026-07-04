from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]

in_path = ROOT / "results" / "rq3_full" / "rq3_final_tradeoff_table.csv"
out_dir = ROOT / "results" / "rq3_full"
out_dir.mkdir(parents=True, exist_ok=True)

if not in_path.exists():
    raise FileNotFoundError(f"Missing input file: {in_path}")

df = pd.read_csv(in_path)

print("Available columns:")
for c in df.columns:
    print(" ", c)

required_cols = [
    "original_family",
    "k_variables",
    "extraction_strategy",
    "mean_weighted_edge_preservation",
    "mean_pct_depth_reduction_vs_original",
    "mean_pct_twoq_reduction_vs_original",
    "mean_pct_swap_reduction_vs_original",
    "mean_normalized_energy_gap_vs_reference",
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns: {missing}")

family_col = "original_family"
k_col = "k_variables"
strategy_col = "extraction_strategy"

pres_col = "mean_weighted_edge_preservation"
depth_red_col = "mean_pct_depth_reduction_vs_original"
twoq_red_col = "mean_pct_twoq_reduction_vs_original"
swap_red_col = "mean_pct_swap_reduction_vs_original"
quality_gap_col = "mean_normalized_energy_gap_vs_reference"

# ---------------------------------------------------------------------
# 1. Spearman trade-off validation
# ---------------------------------------------------------------------

def spearman_row(x_col, y_col, relationship, scope_label, data):
    sub = data[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()
    n = len(sub)

    if n < 3:
        rho, p = np.nan, np.nan
    else:
        rho, p = spearmanr(sub[x_col], sub[y_col])

    return {
        "scope": scope_label,
        "relationship": relationship,
        "x": x_col,
        "y": y_col,
        "n": n,
        "spearman_rho": rho,
        "p_value": p,
    }

spearman_rows = []

# Global relationships.
global_relationships = [
    (pres_col, depth_red_col, "weighted-edge preservation vs depth reduction"),
    (pres_col, twoq_red_col, "weighted-edge preservation vs two-qubit reduction"),
    (pres_col, swap_red_col, "weighted-edge preservation vs SWAP reduction"),
    (pres_col, quality_gap_col, "weighted-edge preservation vs normalized lifted-solution gap"),
    (k_col, pres_col, "sub-QUBO size k vs weighted-edge preservation"),
    (k_col, depth_red_col, "sub-QUBO size k vs depth reduction"),
    (k_col, twoq_red_col, "sub-QUBO size k vs two-qubit reduction"),
    (k_col, swap_red_col, "sub-QUBO size k vs SWAP reduction"),
    (k_col, quality_gap_col, "sub-QUBO size k vs normalized lifted-solution gap"),
]

for x_col, y_col, rel in global_relationships:
    spearman_rows.append(
        spearman_row(x_col, y_col, rel, "all_families", df)
    )

# Family-specific relationships: useful for checking whether global
# trade-off direction is consistent across QUBO families.
for fam, fam_df in df.groupby(family_col):
    for x_col, y_col, rel in [
        (pres_col, twoq_red_col, "weighted-edge preservation vs two-qubit reduction"),
        (pres_col, swap_red_col, "weighted-edge preservation vs SWAP reduction"),
        (pres_col, quality_gap_col, "weighted-edge preservation vs normalized lifted-solution gap"),
        (k_col, pres_col, "sub-QUBO size k vs weighted-edge preservation"),
        (k_col, twoq_red_col, "sub-QUBO size k vs two-qubit reduction"),
        (k_col, swap_red_col, "sub-QUBO size k vs SWAP reduction"),
    ]:
        spearman_rows.append(
            spearman_row(x_col, y_col, rel, f"family={fam}", fam_df)
        )

spearman_df = pd.DataFrame(spearman_rows)

spearman_path = out_dir / "table_rq3_spearman_tradeoff_validation.csv"
spearman_df.to_csv(spearman_path, index=False)

# ---------------------------------------------------------------------
# 2. Pareto analysis
# ---------------------------------------------------------------------

def pareto_efficient_maximize(values):
    """
    Return boolean mask of Pareto-efficient rows.
    All objectives are assumed to be maximized.
    A row is dominated if another row is >= on all objectives
    and > on at least one objective.
    """
    values = np.asarray(values, dtype=float)
    n = values.shape[0]
    efficient = np.ones(n, dtype=bool)

    for i in range(n):
        if not efficient[i]:
            continue

        # Rows that dominate row i
        dominates_i = np.all(values >= values[i], axis=1) & np.any(values > values[i], axis=1)
        dominates_i[i] = False

        if np.any(dominates_i):
            efficient[i] = False

    return efficient

pareto_df = df.copy()

# Circuit-executability profile:
# maximize preservation and all circuit reductions.
circuit_objectives = [
    pres_col,
    depth_red_col,
    twoq_red_col,
    swap_red_col,
]

circuit_data = pareto_df[circuit_objectives].replace([np.inf, -np.inf], np.nan).dropna()
circuit_idx = circuit_data.index
circuit_mask = pareto_efficient_maximize(circuit_data.values)

pareto_df["pareto_circuit_profile"] = False
pareto_df.loc[circuit_idx, "pareto_circuit_profile"] = circuit_mask

# Full readiness profile:
# maximize preservation and circuit reductions, minimize quality gap.
# Minimization is handled by maximizing negative gap.
full_df = pareto_df[
    [pres_col, depth_red_col, twoq_red_col, swap_red_col, quality_gap_col]
].replace([np.inf, -np.inf], np.nan).dropna()

full_idx = full_df.index
full_values = full_df[[pres_col, depth_red_col, twoq_red_col, swap_red_col]].copy()
full_values["negative_quality_gap"] = -full_df[quality_gap_col]

full_mask = pareto_efficient_maximize(full_values.values)

pareto_df["pareto_full_profile"] = False
pareto_df.loc[full_idx, "pareto_full_profile"] = full_mask

pareto_points_path = out_dir / "table_rq3_pareto_points.csv"
pareto_df.to_csv(pareto_points_path, index=False)

# Frequency by extraction strategy.
freq_rows = []
for profile_col in ["pareto_circuit_profile", "pareto_full_profile"]:
    total_pareto = int(pareto_df[profile_col].sum())

    grouped = (
        pareto_df
        .groupby(strategy_col)
        .agg(
            n_rows=(profile_col, "size"),
            n_pareto=(profile_col, "sum")
        )
        .reset_index()
    )

    grouped["profile"] = profile_col
    grouped["within_strategy_pareto_rate"] = grouped["n_pareto"] / grouped["n_rows"]
    grouped["share_of_all_pareto_points"] = grouped["n_pareto"] / total_pareto if total_pareto > 0 else np.nan

    freq_rows.append(grouped)

pareto_freq_strategy_df = pd.concat(freq_rows, ignore_index=True)

pareto_freq_strategy_path = out_dir / "table_rq3_pareto_frequency_by_strategy.csv"
pareto_freq_strategy_df.to_csv(pareto_freq_strategy_path, index=False)

# Frequency by extraction strategy and k.
freq_k_rows = []
for profile_col in ["pareto_circuit_profile", "pareto_full_profile"]:
    total_pareto = int(pareto_df[profile_col].sum())

    grouped = (
        pareto_df
        .groupby([strategy_col, k_col])
        .agg(
            n_rows=(profile_col, "size"),
            n_pareto=(profile_col, "sum")
        )
        .reset_index()
    )

    grouped["profile"] = profile_col
    grouped["within_strategy_k_pareto_rate"] = grouped["n_pareto"] / grouped["n_rows"]
    grouped["share_of_all_pareto_points"] = grouped["n_pareto"] / total_pareto if total_pareto > 0 else np.nan

    freq_k_rows.append(grouped)

pareto_freq_strategy_k_df = pd.concat(freq_k_rows, ignore_index=True)

pareto_freq_strategy_k_path = out_dir / "table_rq3_pareto_frequency_by_strategy_k.csv"
pareto_freq_strategy_k_df.to_csv(pareto_freq_strategy_k_path, index=False)

# ---------------------------------------------------------------------
# 3. Strategy/k descriptive summary
# ---------------------------------------------------------------------

strategy_k_summary = (
    df
    .groupby([strategy_col, k_col])
    .agg(
        n_cells=(pres_col, "size"),
        mean_weighted_edge_preservation=(pres_col, "mean"),
        mean_depth_reduction=(depth_red_col, "mean"),
        mean_twoq_reduction=(twoq_red_col, "mean"),
        mean_swap_reduction=(swap_red_col, "mean"),
        mean_normalized_quality_gap=(quality_gap_col, "mean"),
    )
    .reset_index()
)

strategy_k_summary_path = out_dir / "table_rq3_strategy_k_summary.csv"
strategy_k_summary.to_csv(strategy_k_summary_path, index=False)

# ---------------------------------------------------------------------
# 4. Markdown/text summary without tabulate dependency
# ---------------------------------------------------------------------

summary_path = out_dir / "rq3_statistical_validation_summary.md"

with open(summary_path, "w") as f:
    f.write("# RQ3 statistical validation summary\n\n")

    f.write("## Spearman trade-off validation\n\n")
    f.write(spearman_df.to_string(index=False))
    f.write("\n\n")

    f.write("## Pareto frequency by extraction strategy\n\n")
    f.write(pareto_freq_strategy_df.to_string(index=False))
    f.write("\n\n")

    f.write("## Pareto frequency by extraction strategy and k\n\n")
    f.write(pareto_freq_strategy_k_df.to_string(index=False))
    f.write("\n\n")

    f.write("## Strategy-by-k descriptive summary\n\n")
    f.write(strategy_k_summary.to_string(index=False))
    f.write("\n")

print("\nSaved:")
print(spearman_path)
print(pareto_points_path)
print(pareto_freq_strategy_path)
print(pareto_freq_strategy_k_path)
print(strategy_k_summary_path)
print(summary_path)

print("\nSpearman validation:")
print(spearman_df)

print("\nPareto frequency by strategy:")
print(pareto_freq_strategy_df)

print("\nPareto frequency by strategy and k:")
print(pareto_freq_strategy_k_df)

print("\nStrategy-k summary:")
print(strategy_k_summary)
