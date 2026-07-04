"""
Run pre-transpile QAOA circuit metric extraction for RQ1 pilot.

This script:
1. Reads results/rq1_pilot/graph_metrics.csv.
2. Loads each saved QUBO JSON file.
3. Builds a p=1 QAOA-style circuit.
4. Extracts pre-transpile circuit metrics.
5. Saves results/rq1_pilot/pre_transpile_circuit_metrics.csv.

No transpilation is performed in this step.
"""

from __future__ import annotations

from pathlib import Path
import sys
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


from src.qubo_io import load_qubo_json
from src.qaoa_circuits import (
    build_qaoa_p1_circuit,
    circuit_basic_metrics,
)


GRAPH_METRICS_PATH = PROJECT_ROOT / "results" / "rq1_pilot" / "graph_metrics.csv"
RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_pilot"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)

    rows = []

    gamma = 0.7
    beta = 0.3
    p = 1

    for _, row in graph_df.iterrows():
        qubo_path = PROJECT_ROOT / row["qubo_json"]
        qubo = load_qubo_json(qubo_path)

        circuit = build_qaoa_p1_circuit(
            qubo,
            gamma=gamma,
            beta=beta,
            include_barriers=True,
        )

        metrics = circuit_basic_metrics(circuit)

        output_row = {
            "instance_name": qubo["name"],
            "family": qubo["family"],
            "n_variables": qubo["n_variables"],
            "n_quadratic_terms": len(qubo["quadratic"]),
            "p": p,
            "gamma": gamma,
            "beta": beta,
            "pre_transpile_n_qubits": metrics["n_qubits"],
            "pre_transpile_depth": metrics["depth"],
            "pre_transpile_gate_count": metrics["gate_count"],
            "pre_transpile_2q_count": metrics["two_qubit_gate_count"],
            "pre_transpile_ops_json": json.dumps(metrics["ops"], sort_keys=True),
            "qubo_json": row["qubo_json"],
        }

        rows.append(output_row)

    out_df = pd.DataFrame(rows)

    output_path = RESULTS_DIR / "pre_transpile_circuit_metrics.csv"
    out_df.to_csv(output_path, index=False)

    print("=" * 80)
    print("Pre-transpile QAOA circuit metrics saved")
    print("=" * 80)
    print(f"output: {output_path}")
    print(f"n_instances: {len(out_df)}")
    print()
    print("family counts:")
    print(out_df["family"].value_counts())
    print()
    print("preview:")
    print(
        out_df[
            [
                "instance_name",
                "family",
                "n_variables",
                "n_quadratic_terms",
                "pre_transpile_depth",
                "pre_transpile_gate_count",
                "pre_transpile_2q_count",
            ]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    main()
