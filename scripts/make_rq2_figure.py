from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

csv_path = ROOT / "results" / "rq2_full" / "rq2_mapping_metrics.csv"
out_path = ROOT / "figures" / "fig_rq2_strategy_comparison.png"
out_path.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(csv_path)

strategy_col = "strategy_name"
depth_col = "transpiled_depth"
twoq_col = "transpiled_2q_count"
swap_col = "swap_count"

display_names = {
    "standard_qiskit": "Std.",
    "natural_fixed": "Nat.",
    "random_fixed": "Rand.",
    "degree_desc_fixed": "Deg.",
    "weighted_degree_desc_fixed": "W-deg.",
    "degree_desc_centrality_layout": "Deg-cent.",
    "weighted_degree_desc_centrality_layout": "W-deg-cent.",
    "bfs_topology_aware": "BFS",
}

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

present_order = [s for s in strategy_order if s in df[strategy_col].unique()]

def data_by_strategy(metric_col):
    data = []
    labels = []
    for s in present_order:
        vals = df.loc[df[strategy_col] == s, metric_col].dropna().values
        if len(vals) > 0:
            data.append(vals)
            labels.append(display_names.get(s, s))
    return data, labels

fig, axes = plt.subplots(1, 3, figsize=(14, 4), constrained_layout=True)

panels = [
    (depth_col, "(a)", "Transpiled depth"),
    (twoq_col, "(b)", "Two-qubit count"),
    (swap_col, "(c)", "SWAP count"),
]

for ax, (metric_col, panel_label, ylabel) in zip(axes, panels):
    data, labels = data_by_strategy(metric_col)
    ax.boxplot(data, tick_labels=labels, showfliers=False)
    ax.text(
        0.02, 0.96, panel_label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=11
    )
    ax.set_ylabel(ylabel)
    ax.tick_params(axis="x", rotation=35, labelsize=8)
    ax.grid(axis="y", alpha=0.3)

fig.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Saved: {out_path}")
