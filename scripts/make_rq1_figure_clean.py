from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

csv_path = ROOT / "results" / "rq1_extended" / "merged_rq1_metrics_with_alignment.csv"
out_path = ROOT / "figures" / "fig_rq1_graph_topology_complexity.png"
out_path.parent.mkdir(parents=True, exist_ok=True)

if not csv_path.exists():
    raise FileNotFoundError(f"Missing: {csv_path}")

df = pd.read_csv(csv_path)

print("Available columns:")
print(list(df.columns))

def pick_col(candidates):
    for c in candidates:
        if c in df.columns:
            return c
    raise ValueError(f"Cannot find any of these columns: {candidates}")

topology_col = pick_col(["topology", "backend_topology", "topology_name"])
edges_col = pick_col(["n_edges", "num_edges", "n_qubo_edges", "quadratic_terms", "n_quadratic_terms"])
depth_col = pick_col(["transpiled_depth", "depth"])
distance_col = pick_col(["weighted_mean_topology_distance", "mean_weighted_topology_distance"])
swap_col = pick_col(["swap_count", "swaps"])

topology_order = ["fully_connected", "grid_2d", "heavy_hex_like", "line"]
marker_map = {
    "fully_connected": "D",
    "grid_2d": "s",
    "heavy_hex_like": "^",
    "line": "o",
}

fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)

# Panel A
ax = axes[0]
for topo in topology_order:
    sub = df[df[topology_col] == topo]
    if len(sub) == 0:
        continue
    ax.scatter(
        sub[edges_col],
        sub[depth_col],
        marker=marker_map.get(topo, "o"),
        alpha=0.75,
        label=topo
    )

ax.text(
    0.02, 0.96, "(a)",
    transform=ax.transAxes,
    ha="left",
    va="top",
    fontsize=11
)
ax.set_xlabel("Number of QUBO interaction edges")
ax.set_ylabel("Transpiled QAOA circuit depth")
ax.grid(alpha=0.3)
ax.legend(title="Topology", fontsize=8, title_fontsize=9, frameon=True)

# Panel B
ax = axes[1]
for topo in topology_order:
    sub = df[df[topology_col] == topo]
    if len(sub) == 0:
        continue
    ax.scatter(
        sub[distance_col],
        sub[swap_col],
        marker=marker_map.get(topo, "o"),
        alpha=0.75,
        label=topo
    )

ax.text(
    0.02, 0.96, "(b)",
    transform=ax.transAxes,
    ha="left",
    va="top",
    fontsize=11
)
ax.set_xlabel("Weighted mean topology distance")
ax.set_ylabel("SWAP count")
ax.grid(alpha=0.3)
ax.legend(title="Topology", fontsize=8, title_fontsize=9, frameon=True)

fig.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Saved: {out_path}")
