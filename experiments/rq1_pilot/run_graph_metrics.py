"""
Run RQ1 pilot graph-metric extraction.

This script:
1. Generates small MaxCut-style and assignment-style QUBOs.
2. Saves each generated QUBO as JSON.
3. Converts each QUBO to a QUBO interaction graph.
4. Extracts graph descriptors.
5. Saves results/rq1_pilot/graph_metrics.csv.

This is still graph-level only.
QAOA circuit construction and transpilation will come later.
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
)
from src.graph_utils import qubo_to_interaction_graph
from src.graph_metrics import extract_graph_descriptors


DATA_DIR = PROJECT_ROOT / "data" / "instances"
RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_pilot"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def save_qubo_json(qubo, output_path: Path) -> None:
    """
    Save one QUBO instance as JSON.

    JSON does not allow tuple keys such as (i, j), so quadratic keys are saved
    as strings of the form 'i,j'.
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


def build_pilot_instances():
    """
    Build a small RQ1 pilot set.

    Sizes:
        8, 12, 16 variables

    Families:
        MaxCut-style QUBO
        Assignment-style QUBO
    """
    instances = []
    seeds = [101, 202, 303]

    for seed in seeds:
        for n_variables in [8, 12, 16]:
            instances.append(
                generate_maxcut_qubo(
                    n_variables=n_variables,
                    edge_probability=0.30,
                    seed=seed,
                )
            )

            instances.append(
                generate_maxcut_qubo(
                    n_variables=n_variables,
                    edge_probability=0.60,
                    seed=seed,
                )
            )

    assignment_configs = [
        (4, 2),  # 8 variables
        (6, 2),  # 12 variables
        (8, 2),  # 16 variables
    ]

    for seed in seeds:
        for n_items, n_bins in assignment_configs:
            instances.append(
                generate_assignment_qubo(
                    n_items=n_items,
                    n_bins=n_bins,
                    seed=seed,
                    penalty=10.0,
                )
            )

    return instances


def main() -> None:
    rows = []

    instances = build_pilot_instances()

    for qubo in instances:
        qubo_json_path = DATA_DIR / f"{qubo.name}.json"
        save_qubo_json(qubo, qubo_json_path)

        graph = qubo_to_interaction_graph(qubo.to_dict())
        descriptors = extract_graph_descriptors(graph)

        descriptors["seed"] = qubo.metadata.get("seed")
        descriptors["constant"] = qubo.constant
        descriptors["qubo_json"] = str(qubo_json_path.relative_to(PROJECT_ROOT))

        if qubo.family == "maxcut":
            descriptors["edge_probability"] = qubo.metadata.get("edge_probability")
            descriptors["n_items"] = None
            descriptors["n_bins"] = None

        elif qubo.family == "assignment":
            descriptors["edge_probability"] = None
            descriptors["n_items"] = qubo.metadata.get("n_items")
            descriptors["n_bins"] = qubo.metadata.get("n_bins")

        rows.append(descriptors)

    df = pd.DataFrame(rows)

    output_path = RESULTS_DIR / "graph_metrics.csv"
    df.to_csv(output_path, index=False)

    print("=" * 80)
    print("RQ1 graph metrics and QUBO JSON files saved")
    print("=" * 80)
    print(f"graph metrics output: {output_path}")
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
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()
