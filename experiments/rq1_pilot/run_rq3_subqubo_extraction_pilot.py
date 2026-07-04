"""
RQ3 sub-QUBO extraction pilot.

This script extracts sub-QUBOs from selected original QUBO instances and saves:

1. sub-QUBO JSON files
2. interaction-preservation metrics CSV

Input:
    results/rq1_extended/graph_metrics.csv

Outputs:
    data/subqubos_rq3_pilot/*.json
    results/rq3_pilot/subqubo_extraction_metrics.csv

This step does not run solvers or QAOA transpilation yet.
"""

from __future__ import annotations

from pathlib import Path
import sys
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


from src.qubo_io import load_qubo_json
from src.graph_utils import qubo_to_interaction_graph
from src.subqubo_extraction import (
    available_subqubo_strategies,
    select_subqubo_variables,
    extract_subqubo,
    compute_interaction_preservation_metrics,
)


GRAPH_METRICS_PATH = PROJECT_ROOT / "results" / "rq1_extended" / "graph_metrics.csv"

DATA_DIR = PROJECT_ROOT / "data" / "subqubos_rq3_pilot"
RESULTS_DIR = PROJECT_ROOT / "results" / "rq3_pilot"
OUTPUT_PATH = RESULTS_DIR / "subqubo_extraction_metrics.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def save_qubo_json(qubo: dict, output_path: Path) -> None:
    """
    Save a QUBO dictionary to JSON.

    Handles tuple-key quadratic terms by converting them to 'i,j' strings.
    """
    serializable = {
        "name": qubo["name"],
        "family": qubo["family"],
        "n_variables": int(qubo["n_variables"]),
        "linear": {
            str(i): float(value)
            for i, value in qubo["linear"].items()
        },
        "quadratic": {
            f"{i},{j}": float(value)
            for (i, j), value in qubo["quadratic"].items()
        },
        "constant": float(qubo["constant"]),
        "metadata": qubo.get("metadata", {}),
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)


def select_pilot_original_instances(graph_df: pd.DataFrame) -> pd.DataFrame:
    """
    Select a small but representative pilot set.

    Use n = 24 and n = 32 for each family.
    """
    rows = []

    for family in ["maxcut", "assignment", "scheduling_toy"]:
        for n_variables in [24, 32]:
            sub = graph_df[
                (graph_df["family"] == family)
                & (graph_df["n_variables"] == n_variables)
            ].copy()

            if len(sub) == 0:
                raise ValueError(
                    f"No instance found for family={family}, n={n_variables}"
                )

            # Use first available instance per family-size.
            rows.append(sub.iloc[0])

    return pd.DataFrame(rows)


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)
    pilot_df = select_pilot_original_instances(graph_df)

    strategies = available_subqubo_strategies()

    # k values are chosen to make smaller executable subproblems.
    k_values = [8, 12, 16]

    rows = []

    for _, instance_row in pilot_df.iterrows():
        original_qubo = load_qubo_json(PROJECT_ROOT / instance_row["qubo_json"])
        original_graph = qubo_to_interaction_graph(original_qubo)

        for k_variables in k_values:
            if k_variables >= original_qubo["n_variables"]:
                continue

            for strategy in strategies:
                selected = select_subqubo_variables(
                    qubo_graph=original_graph,
                    k_variables=k_variables,
                    strategy=strategy,
                    seed=123,
                )

                subqubo = extract_subqubo(
                    qubo=original_qubo,
                    selected_variables=selected,
                    new_name_suffix=f"sub_{strategy}_k{k_variables}",
                )

                metrics = compute_interaction_preservation_metrics(
                    qubo=original_qubo,
                    subqubo=subqubo,
                )

                output_json = DATA_DIR / f"{subqubo['name']}.json"
                save_qubo_json(subqubo, output_json)

                row = {
                    "original_instance_name": original_qubo["name"],
                    "original_family": original_qubo["family"],
                    "original_n_variables": original_qubo["n_variables"],
                    "original_n_edges": len(original_qubo["quadratic"]),
                    "original_qubo_json": instance_row["qubo_json"],

                    "subqubo_name": subqubo["name"],
                    "subqubo_family": subqubo["family"],
                    "subqubo_n_variables": subqubo["n_variables"],
                    "subqubo_n_edges": len(subqubo["quadratic"]),
                    "subqubo_json": str(output_json.relative_to(PROJECT_ROOT)),

                    "extraction_strategy": strategy,
                    "k_variables": k_variables,
                    "selected_original_variables": json.dumps(selected),

                    **metrics,
                }

                rows.append(row)

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ3 sub-QUBO extraction pilot saved")
    print("=" * 80)
    print(f"output CSV: {OUTPUT_PATH}")
    print(f"sub-QUBO JSON dir: {DATA_DIR}")
    print(f"shape: {out.shape}")
    print()
    print("family counts:")
    print(out["original_family"].value_counts())
    print()
    print("strategy counts:")
    print(out["extraction_strategy"].value_counts())
    print()
    print("k counts:")
    print(out["k_variables"].value_counts().sort_index())
    print()
    print("summary by strategy:")
    print(
        out.groupby("extraction_strategy", as_index=False)
        .agg(
            n_rows=("subqubo_name", "count"),
            mean_variable_preservation=("variable_preservation_ratio", "mean"),
            mean_edge_preservation=("edge_preservation_ratio", "mean"),
            mean_weighted_edge_preservation=("weighted_edge_preservation_ratio", "mean"),
            mean_sub_edges=("subqubo_n_edges", "mean"),
        )
        .round(3)
        .to_string(index=False)
    )
    print()
    print("preview:")
    print(
        out[
            [
                "original_instance_name",
                "original_family",
                "original_n_variables",
                "subqubo_name",
                "k_variables",
                "extraction_strategy",
                "subqubo_n_edges",
                "edge_preservation_ratio",
                "weighted_edge_preservation_ratio",
                "subqubo_json",
            ]
        ].head(12).to_string(index=False)
    )


if __name__ == "__main__":
    main()
