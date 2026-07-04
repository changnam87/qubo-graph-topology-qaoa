from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]

csv_path = ROOT / "results" / "rq3_full" / "rq3_final_tradeoff_table.csv"
out_path = ROOT / "figures" / "fig_rq3_preservation_executability_tradeoff.png"
out_path.parent.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(csv_path)

strategy_col = "extraction_strategy"
k_col = "k_variables"
pres_col = "mean_weighted_edge_preservation"
twoq_red_col = "mean_pct_twoq_reduction_vs_original"
swap_red_col = "mean_pct_swap_reduction_vs_original"

display_names = {
    "top_weight_edges": "Top-weight edges",
    "high_degree_nodes": "High-degree nodes",
    "weighted_degree_nodes": "Weighted-degree nodes",
    "random_nodes": "Random nodes",
}

strategy_order = [
    "top_weight_edges",
    "high_degree_nodes",
    "weighted_degree_nodes",
    "random_nodes",
]

marker_map = {
    8: "o",
    12: "s",
    16: "^",
}

present_strategies = [s for s in strategy_order if s in df[strategy_col].unique()]

fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), constrained_layout=False)

panels = [
    (twoq_red_col, "(a)", "Mean two-qubit reduction vs. original (%)"),
    (swap_red_col, "(b)", "Mean SWAP reduction vs. original (%)"),
]

for ax, (ycol, panel_label, ylabel) in zip(axes, panels):
    for s in present_strategies:
        sub_s = df[df[strategy_col] == s]

        for kval in sorted(sub_s[k_col].dropna().unique()):
            sub = sub_s[sub_s[k_col] == kval]
            marker = marker_map.get(int(kval), "o")

            ax.scatter(
                sub[pres_col],
                sub[ycol],
                marker=marker,
                s=45,
                alpha=0.78,
                label=f"{display_names.get(s, s)}, k={int(kval)}"
            )

    ax.text(
        0.02, 0.96, panel_label,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=11
    )
    ax.set_xlabel("Mean weighted-edge preservation")
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)

handles, labels = axes[1].get_legend_handles_labels()
unique = {}
for h, l in zip(handles, labels):
    if l not in unique:
        unique[l] = h

fig.legend(
    unique.values(),
    unique.keys(),
    loc="lower center",
    bbox_to_anchor=(0.5, -0.08),
    ncol=4,
    fontsize=7,
    frameon=False
)

plt.subplots_adjust(bottom=0.28, top=0.95, wspace=0.25)

fig.savefig(out_path, dpi=300, bbox_inches="tight")
plt.close(fig)

print(f"Saved: {out_path}")
