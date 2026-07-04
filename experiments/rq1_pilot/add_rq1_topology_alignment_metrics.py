"""
Add topology-alignment descriptors to the extended RQ1 merged dataset.

Input:
    results/rq1_extended/merged_rq1_metrics.csv

Output:
    results/rq1_extended/merged_rq1_metrics_with_alignment.csv

Alignment is computed under natural mapping:

    QUBO variable i -> physical qubit i

RQ2 will later compare alternative mappings.
"""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


from src.qubo_io import load_qubo_json
from src.graph_utils import qubo_to_interaction_graph
from src.topologies import get_coupling_map
from src.topology_alignment import compute_topology_alignment_descriptors


RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_extended"

INPUT_PATH = RESULTS_DIR / "merged_rq1_metrics.csv"
OUTPUT_PATH = RESULTS_DIR / "merged_rq1_metrics_with_alignment.csv"


def main() -> None:
    df = pd.read_csv(INPUT_PATH)

    rows = []

    for idx, row in df.iterrows():
        qubo_path = PROJECT_ROOT / row["qubo_json"]
        qubo = load_qubo_json(qubo_path)
        qubo_graph = qubo_to_interaction_graph(qubo)

        coupling_map = get_coupling_map(
            topology_name=row["topology"],
            n_qubits=int(row["n_variables"]),
        )

        alignment = compute_topology_alignment_descriptors(
            qubo_graph=qubo_graph,
            coupling_map=coupling_map,
            mapping=None,  # natural mapping
        )

        new_row = row.to_dict()
        new_row.update(alignment)

        rows.append(new_row)

        if (idx + 1) % 40 == 0:
            print(f"completed {idx + 1}/{len(df)} rows")

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ1 topology-alignment metrics added")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {out.shape}")
    print()
    print("topology-level alignment summary:")
    print(
        out.groupby("topology", as_index=False)
        .agg(
            n_rows=("instance_name", "count"),
            alignment_mean=("topology_alignment_ratio", "mean"),
            weighted_alignment_mean=("weighted_topology_alignment_ratio", "mean"),
            mean_distance=("mean_topology_distance", "mean"),
            weighted_mean_distance=("weighted_mean_topology_distance", "mean"),
            max_distance_mean=("max_topology_distance", "mean"),
            swap_count_mean=("swap_count", "mean"),
            depth_overhead_mean=("depth_overhead", "mean"),
            twoq_overhead_mean=("twoq_overhead", "mean"),
        )
        .to_string(index=False)
    )
    print()
    print("preview:")
    print(
        out[
            [
                "instance_name",
                "family",
                "n_variables",
                "topology",
                "n_edges",
                "topology_alignment_ratio",
                "weighted_topology_alignment_ratio",
                "mean_topology_distance",
                "weighted_mean_topology_distance",
                "swap_count",
                "depth_overhead",
                "twoq_overhead",
            ]
        ].head(12).to_string(index=False)
    )


if __name__ == "__main__":
    main()
