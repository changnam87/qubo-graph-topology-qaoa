from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]

in_path = ROOT / "results" / "rq1_extended" / "merged_rq1_metrics_with_alignment.csv"
out_dir = ROOT / "results" / "rq1_extended"
out_dir.mkdir(parents=True, exist_ok=True)

if not in_path.exists():
    raise FileNotFoundError(f"Missing input file: {in_path}")

df = pd.read_csv(in_path)

print("Available columns:")
for c in df.columns:
    print(" ", c)

def pick_col(candidates, required=True):
    for c in candidates:
        if c in df.columns:
            return c
    if required:
        raise ValueError(f"Cannot find any of these columns: {candidates}")
    return None

family_col = pick_col(["family", "original_family"], required=False)
topology_col = pick_col(["topology", "backend_topology", "topology_name"], required=False)

# Graph descriptors
edges_col = pick_col(["n_edges", "num_edges", "n_qubo_edges", "n_quadratic_terms", "quadratic_terms"], required=False)
density_col = pick_col(["density", "graph_density", "qubo_density"], required=False)
avg_degree_col = pick_col(["avg_degree", "average_degree", "mean_degree"], required=False)
max_degree_col = pick_col(["max_degree", "maximum_degree"], required=False)
weighted_degree_col = pick_col(["mean_weighted_degree", "avg_weighted_degree", "weighted_degree_mean"], required=False)

# Topology-alignment descriptors
align_col = pick_col(["topology_alignment_ratio", "alignment_ratio", "mean_topology_alignment_ratio"], required=False)
dist_col = pick_col(["weighted_mean_topology_distance", "mean_weighted_topology_distance"], required=False)

# Circuit metrics
pre_depth_col = pick_col(["pre_transpile_depth", "pre_depth", "untranspiled_depth"], required=False)
trans_depth_col = pick_col(["transpiled_depth", "depth"], required=False)
twoq_col = pick_col(["transpiled_2q_count", "transpiled_twoq_count", "two_qubit_count", "twoq_count"], required=False)
swap_col = pick_col(["swap_count", "swaps"], required=False)

candidate_pairs = []

def add_pair(x, y, label):
    if x is not None and y is not None:
        candidate_pairs.append((x, y, label))

# Core RQ1 relationships
add_pair(edges_col, pre_depth_col, "QUBO interaction edges vs pre-transpilation depth")
add_pair(edges_col, trans_depth_col, "QUBO interaction edges vs transpiled depth")
add_pair(edges_col, twoq_col, "QUBO interaction edges vs transpiled two-qubit count")
add_pair(density_col, trans_depth_col, "QUBO graph density vs transpiled depth")
add_pair(avg_degree_col, trans_depth_col, "Average degree vs transpiled depth")
add_pair(max_degree_col, trans_depth_col, "Maximum degree vs transpiled depth")
add_pair(weighted_degree_col, trans_depth_col, "Weighted degree vs transpiled depth")
add_pair(align_col, trans_depth_col, "Topology-alignment ratio vs transpiled depth")
add_pair(align_col, swap_col, "Topology-alignment ratio vs SWAP count")
add_pair(dist_col, trans_depth_col, "Weighted mean topology distance vs transpiled depth")
add_pair(dist_col, swap_col, "Weighted mean topology distance vs SWAP count")
add_pair(dist_col, twoq_col, "Weighted mean topology distance vs transpiled two-qubit count")

if not candidate_pairs:
    raise ValueError("No valid candidate correlation pairs found. Check column names above.")

def spearman_row(data, x_col, y_col, relationship, scope):
    sub = data[[x_col, y_col]].replace([np.inf, -np.inf], np.nan).dropna()
    n = len(sub)
    if n < 3:
        rho, p = np.nan, np.nan
    else:
        rho, p = spearmanr(sub[x_col], sub[y_col])
    return {
        "scope": scope,
        "relationship": relationship,
        "x": x_col,
        "y": y_col,
        "n": n,
        "spearman_rho": rho,
        "p_value": p,
    }

rows = []

# Overall correlations
for x, y, label in candidate_pairs:
    rows.append(spearman_row(df, x, y, label, "all_observations"))

# Family-specific correlations, if available
if family_col is not None:
    for fam, fam_df in df.groupby(family_col):
        for x, y, label in candidate_pairs:
            # Avoid overfilling output: keep most important pairs by family
            if label in [
                "QUBO interaction edges vs transpiled depth",
                "Topology-alignment ratio vs SWAP count",
                "Weighted mean topology distance vs SWAP count",
                "Weighted mean topology distance vs transpiled depth",
            ]:
                rows.append(spearman_row(fam_df, x, y, label, f"family={fam}"))

# Sparse-topology-only correlations, if topology column exists.
if topology_col is not None:
    sparse_df = df[~df[topology_col].astype(str).str.contains("fully", case=False, na=False)].copy()
    for x, y, label in candidate_pairs:
        if label in [
            "Topology-alignment ratio vs SWAP count",
            "Weighted mean topology distance vs SWAP count",
            "Weighted mean topology distance vs transpiled depth",
        ]:
            rows.append(spearman_row(sparse_df, x, y, label, "sparse_topologies_only"))

corr_df = pd.DataFrame(rows)

out_path = out_dir / "table_rq1_spearman_correlations.csv"
corr_df.to_csv(out_path, index=False)

summary_path = out_dir / "rq1_statistical_validation_summary.md"
with open(summary_path, "w") as f:
    f.write("# RQ1 statistical validation summary\n\n")
    f.write("## Spearman correlations\n\n")
    f.write(corr_df.to_string(index=False))
    f.write("\n")

print("\nSaved:")
print(out_path)
print(summary_path)

print("\nRQ1 Spearman correlations:")
print(corr_df)
