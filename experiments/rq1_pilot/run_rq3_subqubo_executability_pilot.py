"""
RQ3 sub-QUBO executability pilot.

This script evaluates QAOA/transpilation executability metrics for extracted
sub-QUBOs.

Input:
    results/rq3_pilot/subqubo_extraction_metrics.csv

Output:
    results/rq3_pilot/subqubo_executability_metrics.csv

This step evaluates compilation/executability only.
It does not evaluate classical solution quality yet.
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
from src.topologies import get_coupling_map
from src.transpile_eval import transpile_and_evaluate


EXTRACTION_PATH = PROJECT_ROOT / "results" / "rq3_pilot" / "subqubo_extraction_metrics.csv"

RESULTS_DIR = PROJECT_ROOT / "results" / "rq3_pilot"
OUTPUT_PATH = RESULTS_DIR / "subqubo_executability_metrics.csv"

RQ3_TOPOLOGIES = [
    "line",
    "grid_2d",
    "heavy_hex_like",
]


def main() -> None:
    extraction_df = pd.read_csv(EXTRACTION_PATH)

    gamma = 0.7
    beta = 0.3
    p = 1
    optimization_level = 1
    seed_transpiler = 123

    rows = []

    total_jobs = len(extraction_df) * len(RQ3_TOPOLOGIES)
    job_counter = 0

    for _, row in extraction_df.iterrows():
        subqubo = load_qubo_json(PROJECT_ROOT / row["subqubo_json"])

        circuit = build_qaoa_p1_circuit(
            subqubo,
            gamma=gamma,
            beta=beta,
            include_barriers=True,
        )

        pre_metrics = circuit_basic_metrics(circuit)

        for topology_name in RQ3_TOPOLOGIES:
            job_counter += 1

            coupling_map = get_coupling_map(
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
                    initial_layout=None,
                )

                post_metrics = result["metrics"]

                output_row = {
                    "original_instance_name": row["original_instance_name"],
                    "original_family": row["original_family"],
                    "original_n_variables": row["original_n_variables"],
                    "original_n_edges": row["original_n_edges"],

                    "subqubo_name": row["subqubo_name"],
                    "subqubo_json": row["subqubo_json"],
                    "subqubo_n_variables": row["subqubo_n_variables"],
                    "subqubo_n_edges": row["subqubo_n_edges"],

                    "extraction_strategy": row["extraction_strategy"],
                    "k_variables": row["k_variables"],

                    "variable_preservation_ratio": row["variable_preservation_ratio"],
                    "edge_preservation_ratio": row["edge_preservation_ratio"],
                    "weighted_edge_preservation_ratio": row["weighted_edge_preservation_ratio"],

                    "p": p,
                    "gamma": gamma,
                    "beta": beta,

                    "topology": topology_name,
                    "optimization_level": optimization_level,
                    "seed_transpiler": seed_transpiler,

                    "pre_transpile_depth": pre_metrics["depth"],
                    "pre_transpile_gate_count": pre_metrics["gate_count"],
                    "pre_transpile_2q_count": pre_metrics["two_qubit_gate_count"],
                    "pre_transpile_ops_json": json.dumps(pre_metrics["ops"], sort_keys=True),

                    "transpiled_depth": post_metrics["transpiled_depth"],
                    "transpiled_gate_count": post_metrics["transpiled_gate_count"],
                    "transpiled_2q_count": post_metrics["transpiled_2q_count"],
                    "swap_count": post_metrics["swap_count"],
                    "cx_count": post_metrics["cx_count"],
                    "transpilation_time_sec": post_metrics["transpilation_time_sec"],
                    "transpiled_ops_json": json.dumps(post_metrics["transpiled_ops"], sort_keys=True),

                    "depth_overhead": post_metrics["transpiled_depth"] / pre_metrics["depth"],
                    "twoq_overhead": (
                        post_metrics["transpiled_2q_count"] / pre_metrics["two_qubit_gate_count"]
                        if pre_metrics["two_qubit_gate_count"] > 0 else None
                    ),

                    "failure_flag": False,
                    "failure_message": "",
                }

            except Exception as exc:
                output_row = {
                    "original_instance_name": row["original_instance_name"],
                    "original_family": row["original_family"],
                    "original_n_variables": row["original_n_variables"],
                    "original_n_edges": row["original_n_edges"],

                    "subqubo_name": row["subqubo_name"],
                    "subqubo_json": row["subqubo_json"],
                    "subqubo_n_variables": row["subqubo_n_variables"],
                    "subqubo_n_edges": row["subqubo_n_edges"],

                    "extraction_strategy": row["extraction_strategy"],
                    "k_variables": row["k_variables"],

                    "variable_preservation_ratio": row["variable_preservation_ratio"],
                    "edge_preservation_ratio": row["edge_preservation_ratio"],
                    "weighted_edge_preservation_ratio": row["weighted_edge_preservation_ratio"],

                    "p": p,
                    "gamma": gamma,
                    "beta": beta,

                    "topology": topology_name,
                    "optimization_level": optimization_level,
                    "seed_transpiler": seed_transpiler,

                    "pre_transpile_depth": None,
                    "pre_transpile_gate_count": None,
                    "pre_transpile_2q_count": None,
                    "pre_transpile_ops_json": None,

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

            if job_counter % 36 == 0:
                print(f"completed {job_counter}/{total_jobs}")

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ3 sub-QUBO executability metrics saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {out.shape}")
    print()
    print("failure counts:")
    print(out["failure_flag"].value_counts())
    print()
    print("topology counts:")
    print(out["topology"].value_counts())
    print()
    print("strategy counts:")
    print(out["extraction_strategy"].value_counts())
    print()
    print("summary by strategy:")
    print(
        out.groupby("extraction_strategy", as_index=False)
        .agg(
            n_rows=("subqubo_name", "count"),
            mean_weighted_edge_preservation=("weighted_edge_preservation_ratio", "mean"),
            mean_pre_depth=("pre_transpile_depth", "mean"),
            mean_transpiled_depth=("transpiled_depth", "mean"),
            mean_2q=("transpiled_2q_count", "mean"),
            mean_swap=("swap_count", "mean"),
            mean_depth_overhead=("depth_overhead", "mean"),
            mean_twoq_overhead=("twoq_overhead", "mean"),
        )
        .round(3)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
