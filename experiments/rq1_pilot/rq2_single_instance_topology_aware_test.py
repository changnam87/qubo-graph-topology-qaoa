"""
RQ2 single-instance topology-aware placement test.

This script compares three layout modes:

1. standard_qiskit
   - initial_layout = None

2. fixed_identity_after_relabeling
   - relabel QUBO by ordering
   - initial_layout = [0, 1, ..., n-1]

3. topology_aware_centrality
   - relabel QUBO by ordering
   - circuit qubit 0,1,2,... are placed on central physical qubits first

Input:
    results/rq1_extended/graph_metrics.csv

Output:
    results/rq2_pilot/single_instance_topology_aware_comparison.csv
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
)
from src.qubo_relabeling import relabel_qubo_by_ordering
from src.qaoa_circuits import build_qaoa_p1_circuit, circuit_basic_metrics
from src.topologies import get_coupling_map
from src.transpile_eval import transpile_and_evaluate


GRAPH_METRICS_PATH = PROJECT_ROOT / "results" / "rq1_extended" / "graph_metrics.csv"
RESULTS_DIR = PROJECT_ROOT / "results" / "rq2_pilot"
OUTPUT_PATH = RESULTS_DIR / "single_instance_topology_aware_comparison.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


ORDERING_STRATEGIES = [
    "degree_desc",
    "weighted_degree_desc",
]

LAYOUT_MODES = [
    "standard_qiskit",
    "fixed_identity_after_relabeling",
    "topology_aware_centrality",
]


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)

    # Use one scheduling-derived instance where ordering showed potential benefit.
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
        ordering = get_variable_ordering(
            original_graph,
            strategy=ordering_strategy,
            seed=123,
        )

        relabeled_qubo = relabel_qubo_by_ordering(
            original_qubo,
            ordering=ordering,
            new_name_suffix=ordering_strategy,
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

        for layout_mode in LAYOUT_MODES:
            if layout_mode == "standard_qiskit":
                initial_layout = None

            elif layout_mode == "fixed_identity_after_relabeling":
                initial_layout = list(range(circuit.num_qubits))

            elif layout_mode == "topology_aware_centrality":
                initial_layout = build_topology_aware_initial_layout(
                    n_qubits=circuit.num_qubits,
                    coupling_map=coupling_map,
                    physical_strategy="centrality_desc",
                )

            else:
                raise ValueError(f"Unknown layout_mode: {layout_mode}")

            result = transpile_and_evaluate(
                circuit=circuit,
                coupling_map=coupling_map,
                topology_name=topology_name,
                optimization_level=optimization_level,
                seed_transpiler=seed_transpiler,
                initial_layout=initial_layout,
            )

            post_metrics = result["metrics"]

            rows.append(
                {
                    "original_instance_name": original_qubo["name"],
                    "family": original_qubo["family"],
                    "n_variables": original_qubo["n_variables"],
                    "n_quadratic_terms": len(original_qubo["quadratic"]),

                    "ordering_strategy": ordering_strategy,
                    "ordering": json.dumps(ordering),

                    "layout_mode": layout_mode,
                    "initial_layout": json.dumps(initial_layout),

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

    # Compare against fixed identity within each ordering strategy.
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
    print("RQ2 single-instance topology-aware placement comparison saved")
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
