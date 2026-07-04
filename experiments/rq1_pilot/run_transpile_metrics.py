"""
Run topology-aware transpilation metric extraction for RQ1 pilot.

This script:
1. Reads results/rq1_pilot/graph_metrics.csv.
2. Loads each saved QUBO JSON file.
3. Builds a p=1 QAOA-style circuit.
4. Transpiles each circuit to each local topology.
5. Saves results/rq1_pilot/transpile_metrics.csv.

Topologies:
    - line
    - grid_2d
    - heavy_hex_like
    - fully_connected
"""

from __future__ import annotations

from pathlib import Path
import sys
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


from src.qubo_io import load_qubo_json
from src.qaoa_circuits import build_qaoa_p1_circuit, circuit_basic_metrics
from src.topologies import available_topologies, get_coupling_map, coupling_map_summary
from src.transpile_eval import transpile_and_evaluate


GRAPH_METRICS_PATH = PROJECT_ROOT / "results" / "rq1_pilot" / "graph_metrics.csv"
RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_pilot"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)

    rows = []

    gamma = 0.7
    beta = 0.3
    p = 1
    optimization_level = 1
    seed_transpiler = 123

    for _, row in graph_df.iterrows():
        qubo_path = PROJECT_ROOT / row["qubo_json"]
        qubo = load_qubo_json(qubo_path)

        circuit = build_qaoa_p1_circuit(
            qubo,
            gamma=gamma,
            beta=beta,
            include_barriers=True,
        )

        pre_metrics = circuit_basic_metrics(circuit)

        for topology_name in available_topologies():
            coupling_map = get_coupling_map(
                topology_name=topology_name,
                n_qubits=circuit.num_qubits,
            )

            topology_summary = coupling_map_summary(
                topology_name=topology_name,
                n_qubits=circuit.num_qubits,
            )

            try:
                result = transpile_and_evaluate(
                    circuit=circuit,
                    coupling_map=coupling_map,
                    topology_name=topology_name,
                    optimization_level=optimization_level,
                    seed_transpiler=seed_transpiler,
                )

                post_metrics = result["metrics"]

                failure_flag = False
                failure_message = ""

                output_row = {
                    "instance_name": qubo["name"],
                    "family": qubo["family"],
                    "n_variables": qubo["n_variables"],
                    "n_quadratic_terms": len(qubo["quadratic"]),
                    "qubo_json": row["qubo_json"],

                    "p": p,
                    "gamma": gamma,
                    "beta": beta,

                    "topology": topology_name,
                    "topology_n_directed_edges": topology_summary["n_directed_edges"],
                    "topology_n_undirected_edges": topology_summary["n_undirected_edges"],
                    "topology_is_connected": topology_summary["is_connected"],

                    "optimization_level": optimization_level,
                    "seed_transpiler": seed_transpiler,

                    "pre_transpile_n_qubits": pre_metrics["n_qubits"],
                    "pre_transpile_depth": pre_metrics["depth"],
                    "pre_transpile_gate_count": pre_metrics["gate_count"],
                    "pre_transpile_2q_count": pre_metrics["two_qubit_gate_count"],
                    "pre_transpile_ops_json": json.dumps(pre_metrics["ops"], sort_keys=True),

                    "transpiled_n_qubits": post_metrics["transpiled_n_qubits"],
                    "transpiled_depth": post_metrics["transpiled_depth"],
                    "transpiled_gate_count": post_metrics["transpiled_gate_count"],
                    "transpiled_2q_count": post_metrics["transpiled_2q_count"],
                    "swap_count": post_metrics["swap_count"],
                    "cx_count": post_metrics["cx_count"],
                    "transpilation_time_sec": post_metrics["transpilation_time_sec"],
                    "transpiled_ops_json": json.dumps(post_metrics["transpiled_ops"], sort_keys=True),

                    "depth_overhead": post_metrics["transpiled_depth"] / pre_metrics["depth"],
                    "twoq_overhead": post_metrics["transpiled_2q_count"] / pre_metrics["two_qubit_gate_count"]
                    if pre_metrics["two_qubit_gate_count"] > 0 else None,

                    "failure_flag": failure_flag,
                    "failure_message": failure_message,
                }

            except Exception as exc:
                output_row = {
                    "instance_name": qubo["name"],
                    "family": qubo["family"],
                    "n_variables": qubo["n_variables"],
                    "n_quadratic_terms": len(qubo["quadratic"]),
                    "qubo_json": row["qubo_json"],

                    "p": p,
                    "gamma": gamma,
                    "beta": beta,

                    "topology": topology_name,
                    "topology_n_directed_edges": topology_summary["n_directed_edges"],
                    "topology_n_undirected_edges": topology_summary["n_undirected_edges"],
                    "topology_is_connected": topology_summary["is_connected"],

                    "optimization_level": optimization_level,
                    "seed_transpiler": seed_transpiler,

                    "pre_transpile_n_qubits": pre_metrics["n_qubits"],
                    "pre_transpile_depth": pre_metrics["depth"],
                    "pre_transpile_gate_count": pre_metrics["gate_count"],
                    "pre_transpile_2q_count": pre_metrics["two_qubit_gate_count"],
                    "pre_transpile_ops_json": json.dumps(pre_metrics["ops"], sort_keys=True),

                    "transpiled_n_qubits": None,
                    "transpiled_depth": None,
                    "transpiled_gate_count": None,
                    "transpiled_2q_count": None,
                    "swap_count": None,
                    "cx_count": None,
                    "transpilation_time_sec": None,
                    "transpiled_ops_json": None,

                    "depth_overhead": None,
                    "twoq_overhead": None,

                    "failure_flag": True,
                    "failure_message": str(exc),
                }

            rows.append(output_row)

    out_df = pd.DataFrame(rows)

    output_path = RESULTS_DIR / "transpile_metrics.csv"
    out_df.to_csv(output_path, index=False)

    print("=" * 80)
    print("Topology-aware transpilation metrics saved")
    print("=" * 80)
    print(f"output: {output_path}")
    print(f"n_rows: {len(out_df)}")
    print()
    print("topology counts:")
    print(out_df["topology"].value_counts())
    print()
    print("failure counts:")
    print(out_df["failure_flag"].value_counts())
    print()
    print("preview:")
    print(
        out_df[
            [
                "instance_name",
                "family",
                "n_variables",
                "topology",
                "pre_transpile_depth",
                "transpiled_depth",
                "pre_transpile_2q_count",
                "transpiled_2q_count",
                "swap_count",
                "depth_overhead",
                "twoq_overhead",
                "failure_flag",
            ]
        ].head(12).to_string(index=False)
    )


if __name__ == "__main__":
    main()
