"""
Generate the extended RQ1 QUBO dataset and graph metrics.

This script expands the pilot dataset by adding:
1. Larger sizes: 8, 12, 16, 24, 32 variables
2. A third QUBO family: scheduling_toy

Outputs:
    data/instances_rq1_extended/*.json
    results/rq1_extended/graph_metrics.csv
"""

from __future__ import annotations

from pathlib import Path
import sys
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


from src.qubo_generators import (
    generate_maxcut_qubo,
    generate_assignment_qubo,
    generate_scheduling_toy_qubo,
)
from src.graph_utils import qubo_to_interaction_graph
from src.graph_metrics import extract_graph_descriptors


DATA_DIR = PROJECT_ROOT / "data" / "instances_rq1_extended"
RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_extended"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def save_qubo_json(qubo, output_path: Path) -> None:
    """
    Save one QUBO instance as JSON.
    """
    serializable = {
        "name": qubo.name,
        "family": qubo.family,
        "n_variables": qubo.n_variables,
        "linear": {
            str(i): float(value)
            for i, value in qubo.linear.items()
        },
        "quadratic": {
            f"{i},{j}": float(value)
            for (i, j), value in qubo.quadratic.items()
        },
        "constant": float(qubo.constant),
        "metadata": qubo.metadata,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)


def build_extended_instances():
    """
    Build extended RQ1 instances.

    Target variable sizes:
        8, 12, 16, 24, 32

    Families:
        maxcut
        assignment
        scheduling_toy
    """
    instances = []

    seeds = [101, 202, 303]
    sizes = [8, 12, 16, 24, 32]

    # ------------------------------------------------------------
    # 1. MaxCut-style QUBOs
    # ------------------------------------------------------------
    for seed in seeds:
        for n_variables in sizes:
            for edge_probability in [0.30, 0.60]:
                instances.append(
                    generate_maxcut_qubo(
                        n_variables=n_variables,
                        edge_probability=edge_probability,
                        seed=seed,
                    )
                )

    # ------------------------------------------------------------
    # 2. Assignment-style QUBOs
    #    Use n_bins = 2, so n_items = n_variables / 2.
    # ------------------------------------------------------------
    for seed in seeds:
        for n_variables in sizes:
            n_items = n_variables // 2
            n_bins = 2

            instances.append(
                generate_assignment_qubo(
                    n_items=n_items,
                    n_bins=n_bins,
                    seed=seed,
                    penalty=10.0,
                )
            )

    # ------------------------------------------------------------
    # 3. Scheduling-derived toy QUBOs
    #    Use n_machines = 2, so n_operations = n_variables / 2.
    # ------------------------------------------------------------
    for seed in seeds:
        for n_variables in sizes:
            n_operations = n_variables // 2
            n_machines = 2

            instances.append(
                generate_scheduling_toy_qubo(
                    n_operations=n_operations,
                    n_machines=n_machines,
                    seed=seed,
                    assignment_penalty=10.0,
                    conflict_penalty=6.0,
                    conflict_probability=0.35,
                )
            )

    return instances


def add_family_specific_metadata(descriptors, qubo):
    """
    Add family-specific metadata columns to the graph metric row.
    """
    descriptors["seed"] = qubo.metadata.get("seed")
    descriptors["constant"] = qubo.constant

    descriptors["edge_probability"] = None
    descriptors["n_items"] = None
    descriptors["n_bins"] = None
    descriptors["n_operations"] = None
    descriptors["n_machines"] = None
    descriptors["conflict_probability"] = None
    descriptors["n_conflict_pairs"] = None

    if qubo.family == "maxcut":
        descriptors["edge_probability"] = qubo.metadata.get("edge_probability")

    elif qubo.family == "assignment":
        descriptors["n_items"] = qubo.metadata.get("n_items")
        descriptors["n_bins"] = qubo.metadata.get("n_bins")

    elif qubo.family == "scheduling_toy":
        descriptors["n_operations"] = qubo.metadata.get("n_operations")
        descriptors["n_machines"] = qubo.metadata.get("n_machines")
        descriptors["conflict_probability"] = qubo.metadata.get("conflict_probability")
        descriptors["n_conflict_pairs"] = len(qubo.metadata.get("conflict_pairs", []))

    return descriptors


def main() -> None:
    instances = build_extended_instances()
    rows = []

    for qubo in instances:
        qubo_json_path = DATA_DIR / f"{qubo.name}.json"
        save_qubo_json(qubo, qubo_json_path)

        graph = qubo_to_interaction_graph(qubo.to_dict())
        descriptors = extract_graph_descriptors(graph)

        descriptors = add_family_specific_metadata(descriptors, qubo)
        descriptors["qubo_json"] = str(qubo_json_path.relative_to(PROJECT_ROOT))

        rows.append(descriptors)

    df = pd.DataFrame(rows)

    output_path = RESULTS_DIR / "graph_metrics.csv"
    df.to_csv(output_path, index=False)

    print("=" * 80)
    print("RQ1 extended graph metrics saved")
    print("=" * 80)
    print(f"output: {output_path}")
    print(f"QUBO JSON directory: {DATA_DIR}")
    print(f"n_instances: {len(df)}")
    print()
    print("family counts:")
    print(df["family"].value_counts())
    print()
    print("variable-size counts:")
    print(df["n_variables"].value_counts().sort_index())
    print()
    print("preview:")
    print(
        df[
            [
                "instance_name",
                "family",
                "n_variables",
                "n_edges",
                "density",
                "qubo_json",
            ]
        ].head(12).to_string(index=False)
    )


if __name__ == "__main__":
    main()
