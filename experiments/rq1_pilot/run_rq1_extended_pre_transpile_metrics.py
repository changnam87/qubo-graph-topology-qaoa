"""
Run pre-transpile QAOA circuit metric extraction for the extended RQ1 dataset.

Input:
    results/rq1_extended/graph_metrics.csv

Output:
    results/rq1_extended/pre_transpile_circuit_metrics.csv

This step builds p = 1 QAOA-style circuits only.
No transpilation is performed here.
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


RESULTS_DIR = PROJECT_ROOT / "results" / "rq1_extended"
GRAPH_METRICS_PATH = RESULTS_DIR / "graph_metrics.csv"
OUTPUT_PATH = RESULTS_DIR / "pre_transpile_circuit_metrics.csv"


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

        rows.append(
            {
                "instance_name": qubo["name"],
                "family": qubo["family"],
                "n_variables": qubo["n_variables"],
                "n_quadratic_terms": len(qubo["quadratic"]),
                "qubo_json": row["qubo_json"],

                "p": p,
                "gamma": gamma,
                "beta": beta,

                "pre_transpile_n_qubits": metrics["n_qubits"],
                "pre_transpile_depth": metrics["depth"],
                "pre_transpile_gate_count": metrics["gate_count"],
                "pre_transpile_2q_count": metrics["two_qubit_gate_count"],
                "pre_transpile_ops_json": json.dumps(metrics["ops"], sort_keys=True),
            }
        )

    out_df = pd.DataFrame(rows)
    out_df.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ1 extended pre-transpile circuit metrics saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"n_instances: {len(out_df)}")
    print()
    print("family counts:")
    print(out_df["family"].value_counts())
    print()
    print("variable-size counts:")
    print(out_df["n_variables"].value_counts().sort_index())
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
        ].head(12).to_string(index=False)
    )


if __name__ == "__main__":
    main()
