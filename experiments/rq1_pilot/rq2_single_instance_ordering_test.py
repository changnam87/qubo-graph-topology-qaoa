"""
RQ2 single-instance ordering test.

This script compares variable ordering strategies on one QUBO instance
and one topology.

Input:
    results/rq1_extended/graph_metrics.csv

Output:
    results/rq2_pilot/single_instance_ordering_comparison.csv

Purpose:
    Verify that QUBO relabeling + ordering strategies actually affect
    transpilation metrics.
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
from src.mapping_strategies import (
    available_ordering_strategies,
    get_variable_ordering,
)
from src.qubo_relabeling import relabel_qubo_by_ordering
from src.qaoa_circuits import build_qaoa_p1_circuit, circuit_basic_metrics
from src.topologies import get_coupling_map
from src.transpile_eval import transpile_and_evaluate


GRAPH_METRICS_PATH = PROJECT_ROOT / "results" / "rq1_extended" / "graph_metrics.csv"
RESULTS_DIR = PROJECT_ROOT / "results" / "rq2_pilot"
OUTPUT_PATH = RESULTS_DIR / "single_instance_ordering_comparison.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)

    # Use a moderately sized scheduling-derived instance.
    candidates = graph_df[
        (graph_df["family"] == "scheduling_toy")
        & (graph_df["n_variables"] == 16)
    ].copy()

    if len(candidates) == 0:
        raise ValueError("No scheduling_toy instance with n_variables = 16 found.")

    row = candidates.iloc[0]

    original_qubo = load_qubo_json(PROJECT_ROOT / row["qubo_json"])
    original_graph = qubo_to_interaction_graph(original_qubo)

    topology_name = "line"
    gamma = 0.7
    beta = 0.3
    p = 1
    optimization_level = 1
    seed_transpiler = 123

    rows = []

    for strategy in available_ordering_strategies():
        ordering = get_variable_ordering(
            original_graph,
            strategy=strategy,
            seed=123,
        )

        relabeled_qubo = relabel_qubo_by_ordering(
            original_qubo,
            ordering=ordering,
            new_name_suffix=strategy,
        )

        circuit = build_qaoa_p1_circuit(
            relabeled_qubo,
            gamma=gamma,
            beta=beta,
            include_barriers=True,
        )

        pre_metrics = circuit_basic_metrics(circuit)

        coupling_map = get_coupling_map(
            topology_name=topology_name,
            n_qubits=circuit.num_qubits,
        )

        result = transpile_and_evaluate(
            circuit=circuit,
            coupling_map=coupling_map,
            topology_name=topology_name,
            optimization_level=optimization_level,
            seed_transpiler=seed_transpiler,
        )

        post_metrics = result["metrics"]

        rows.append(
            {
                "original_instance_name": original_qubo["name"],
                "relabeled_instance_name": relabeled_qubo["name"],
                "family": original_qubo["family"],
                "n_variables": original_qubo["n_variables"],
                "n_quadratic_terms": len(original_qubo["quadratic"]),

                "ordering_strategy": strategy,
                "ordering": json.dumps(ordering),

                "p": p,
                "gamma": gamma,
                "beta": beta,

                "topology": topology_name,
                "optimization_level": optimization_level,
                "seed_transpiler": seed_transpiler,

                "pre_transpile_depth": pre_metrics["depth"],
                "pre_transpile_gate_count": pre_metrics["gate_count"],
                "pre_transpile_2q_count": pre_metrics["two_qubit_gate_count"],

                "transpiled_depth": post_metrics["transpiled_depth"],
                "transpiled_gate_count": post_metrics["transpiled_gate_count"],
                "transpiled_2q_count": post_metrics["transpiled_2q_count"],
                "swap_count": post_metrics["swap_count"],
                "cx_count": post_metrics["cx_count"],
                "transpilation_time_sec": post_metrics["transpilation_time_sec"],

                "depth_overhead": post_metrics["transpiled_depth"] / pre_metrics["depth"],
                "twoq_overhead": (
                    post_metrics["transpiled_2q_count"]
                    / pre_metrics["two_qubit_gate_count"]
                    if pre_metrics["two_qubit_gate_count"] > 0
                    else None
                ),

                "transpiled_ops_json": json.dumps(
                    post_metrics["transpiled_ops"],
                    sort_keys=True,
                ),
            }
        )

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ2 single-instance ordering comparison saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print()
    print(
        out[
            [
                "ordering_strategy",
                "n_variables",
                "n_quadratic_terms",
                "topology",
                "pre_transpile_depth",
                "transpiled_depth",
                "transpiled_2q_count",
                "swap_count",
                "depth_overhead",
                "twoq_overhead",
            ]
        ].to_string(index=False)
    )

    print()
    natural = out[out["ordering_strategy"] == "natural"].iloc[0]
    out["delta_depth_vs_natural"] = out["transpiled_depth"] - natural["transpiled_depth"]
    out["delta_swap_vs_natural"] = out["swap_count"] - natural["swap_count"]

    print("Delta vs natural:")
    print(
        out[
            [
                "ordering_strategy",
                "delta_depth_vs_natural",
                "delta_swap_vs_natural",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
