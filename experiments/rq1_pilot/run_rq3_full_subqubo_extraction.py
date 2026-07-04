"""
RQ3 full sub-QUBO extraction experiment.

This script expands the RQ3 pilot to all RQ1 extended instances with
n_variables in {24, 32}.

Input:
    results/rq1_extended/graph_metrics.csv

Outputs:
    data/subqubos_rq3_full/*.json
    results/rq3_full/subqubo_extraction_metrics.csv

Scope:
    Original QUBOs:
        n = 24, 32

        maxcut:
            2 sizes × 2 densities × 3 seeds = 12

        assignment:
            2 sizes × 3 seeds = 6

        scheduling_toy:
            2 sizes × 3 seeds = 6

        total = 24 original QUBOs

    Sub-QUBOs:
        24 originals × 3 k values × 4 strategies = 288
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

DATA_DIR = PROJECT_ROOT / "data" / "subqubos_rq3_full"
RESULTS_DIR = PROJECT_ROOT / "results" / "rq3_full"
OUTPUT_PATH = RESULTS_DIR / "subqubo_extraction_metrics.csv"

DATA_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def save_qubo_json(qubo: dict, output_path: Path) -> None:
    """
    Save a QUBO dictionary to JSON.

    Tuple-key quadratic terms are converted to 'i,j' strings.
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


def select_full_original_instances(graph_df: pd.DataFrame) -> pd.DataFrame:
    """
    Select all original QUBOs with n_variables in {24, 32}.

    This gives:
        maxcut: 12
        assignment: 6
        scheduling_toy: 6
        total: 24
    """
    full_df = graph_df[
        graph_df["n_variables"].isin([24, 32])
    ].copy()

    full_df = full_df.sort_values(
        ["family", "n_variables", "instance_name"]
    ).reset_index(drop=True)

    return full_df


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)
    full_df = select_full_original_instances(graph_df)

    strategies = available_subqubo_strategies()
    k_values = [8, 12, 16]

    rows = []

    expected_originals = 24
    expected_rows = expected_originals * len(k_values) * len(strategies)

    print("=" * 80)
    print("RQ3 full extraction setup")
    print("=" * 80)
    print("selected original QUBOs:", len(full_df))
    print("expected rows:", expected_rows)
    print()
    print("family counts:")
    print(full_df["family"].value_counts())
    print()
    print("size counts:")
    print(full_df["n_variables"].value_counts().sort_index())
    print()

    for idx, instance_row in full_df.iterrows():
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

        if (idx + 1) % 4 == 0:
            print(f"completed original {idx + 1}/{len(full_df)}")

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ3 full sub-QUBO extraction saved")
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
