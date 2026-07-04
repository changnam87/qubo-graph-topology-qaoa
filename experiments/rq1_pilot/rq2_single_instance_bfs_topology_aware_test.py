"""
RQ2 single-instance BFS topology-aware placement test.

This script compares four layout modes:

1. standard_qiskit
   - initial_layout = None

2. fixed_identity_after_relabeling
   - relabel QUBO by graph ordering
   - initial_layout = [0, 1, ..., n-1]

3. topology_aware_centrality
   - relabel QUBO by graph ordering
   - place early circuit qubits on central physical qubits

4. bfs_topology_aware
   - create QUBO BFS ordering
   - relabel QUBO by QUBO BFS ordering
   - place relabeled circuit qubits on topology BFS physical ordering

Input:
    results/rq1_extended/graph_metrics.csv

Output:
    results/rq2_pilot/single_instance_bfs_topology_aware_comparison.csv
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
    get_variable_ordering,
    build_topology_aware_initial_layout,
    build_bfs_topology_aware_initial_layout,
)
from src.qubo_relabeling import relabel_qubo_by_ordering
from src.qaoa_circuits import build_qaoa_p1_circuit, circuit_basic_metrics
from src.topologies import get_coupling_map
from src.transpile_eval import transpile_and_evaluate


GRAPH_METRICS_PATH = PROJECT_ROOT / "results" / "rq1_extended" / "graph_metrics.csv"
RESULTS_DIR = PROJECT_ROOT / "results" / "rq2_pilot"
OUTPUT_PATH = RESULTS_DIR / "single_instance_bfs_topology_aware_comparison.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


ORDERING_STRATEGIES = [
    "degree_desc",
    "weighted_degree_desc",
]

LAYOUT_MODES = [
    "standard_qiskit",
    "fixed_identity_after_relabeling",
    "topology_aware_centrality",
    "bfs_topology_aware",
]


def run_one_condition(
    original_qubo,
    original_graph,
    ordering_strategy: str,
    layout_mode: str,
    topology_name: str,
    gamma: float,
    beta: float,
    p: int,
    optimization_level: int,
    seed_transpiler: int,
):
    """
    Run one ordering-layout condition.
    """
    coupling_map = get_coupling_map(
        topology_name=topology_name,
        n_qubits=original_qubo["n_variables"],
    )

    if layout_mode == "bfs_topology_aware":
        qubo_ordering, physical_ordering, initial_layout = build_bfs_topology_aware_initial_layout(
            qubo_graph=original_graph,
            coupling_map=coupling_map,
        )

        relabeled_qubo = relabel_qubo_by_ordering(
            original_qubo,
            ordering=qubo_ordering,
            new_name_suffix=f"bfs_{topology_name}",
        )

        ordering_used = qubo_ordering
        physical_ordering_used = physical_ordering

    else:
        ordering_used = get_variable_ordering(
            original_graph,
            strategy=ordering_strategy,
            seed=123,
        )

        relabeled_qubo = relabel_qubo_by_ordering(
            original_qubo,
            ordering=ordering_used,
            new_name_suffix=ordering_strategy,
        )

        physical_ordering_used = None

        if layout_mode == "standard_qiskit":
            initial_layout = None

        elif layout_mode == "fixed_identity_after_relabeling":
            initial_layout = list(range(original_qubo["n_variables"]))

        elif layout_mode == "topology_aware_centrality":
            initial_layout = build_topology_aware_initial_layout(
                n_qubits=original_qubo["n_variables"],
                coupling_map=coupling_map,
                physical_strategy="centrality_desc",
            )

        else:
            raise ValueError(f"Unknown layout_mode: {layout_mode}")

    circuit = build_qaoa_p1_circuit(
        relabeled_qubo,
        gamma=gamma,
        beta=beta,
        include_barriers=True,
    )

    pre_metrics = circuit_basic_metrics(circuit)

    result = transpile_and_evaluate(
        circuit=circuit,
        coupling_map=coupling_map,
        topology_name=topology_name,
        optimization_level=optimization_level,
        seed_transpiler=seed_transpiler,
        initial_layout=initial_layout,
    )

    post_metrics = result["metrics"]

    return {
        "ordering_used": ordering_used,
        "physical_ordering_used": physical_ordering_used,
        "initial_layout": initial_layout,
        "pre_metrics": pre_metrics,
        "post_metrics": post_metrics,
    }


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)

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

    for ordering_strategy in ORDERING_STRATEGIES:
        for layout_mode in LAYOUT_MODES:
            result = run_one_condition(
                original_qubo=original_qubo,
                original_graph=original_graph,
                ordering_strategy=ordering_strategy,
                layout_mode=layout_mode,
                topology_name=topology_name,
                gamma=gamma,
                beta=beta,
                p=p,
                optimization_level=optimization_level,
                seed_transpiler=seed_transpiler,
            )

            pre_metrics = result["pre_metrics"]
            post_metrics = result["post_metrics"]

            rows.append(
                {
                    "original_instance_name": original_qubo["name"],
                    "family": original_qubo["family"],
                    "n_variables": original_qubo["n_variables"],
                    "n_quadratic_terms": len(original_qubo["quadratic"]),

                    "ordering_strategy": ordering_strategy,
                    "layout_mode": layout_mode,

                    "ordering_used": json.dumps(result["ordering_used"]),
                    "physical_ordering_used": json.dumps(result["physical_ordering_used"]),
                    "initial_layout": json.dumps(result["initial_layout"]),

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

    baseline = out[out["layout_mode"] == "fixed_identity_after_relabeling"][
        [
            "ordering_strategy",
            "transpiled_depth",
            "transpiled_2q_count",
            "swap_count",
        ]
    ].copy()

    baseline = baseline.rename(
        columns={
            "transpiled_depth": "fixed_identity_depth",
            "transpiled_2q_count": "fixed_identity_2q",
            "swap_count": "fixed_identity_swap",
        }
    )

    out = out.merge(
        baseline,
        on="ordering_strategy",
        how="left",
        validate="many_to_one",
    )

    out["delta_depth_vs_fixed_identity"] = (
        out["transpiled_depth"] - out["fixed_identity_depth"]
    )
    out["delta_2q_vs_fixed_identity"] = (
        out["transpiled_2q_count"] - out["fixed_identity_2q"]
    )
    out["delta_swap_vs_fixed_identity"] = (
        out["swap_count"] - out["fixed_identity_swap"]
    )

    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ2 single-instance BFS topology-aware comparison saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print()
    print(
        out[
            [
                "ordering_strategy",
                "layout_mode",
                "topology",
                "transpiled_depth",
                "transpiled_2q_count",
                "swap_count",
                "depth_overhead",
                "twoq_overhead",
                "delta_depth_vs_fixed_identity",
                "delta_2q_vs_fixed_identity",
                "delta_swap_vs_fixed_identity",
            ]
        ].round(3).to_string(index=False)
    )


if __name__ == "__main__":
    main()
