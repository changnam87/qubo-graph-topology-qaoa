"""
Run full RQ2 mapping-strategy experiment.

Input:
    results/rq1_extended/graph_metrics.csv

Output:
    results/rq2_full/rq2_mapping_metrics.csv

Scope:
    60 QUBO instances
    3 sparse topologies
    8 RQ2 strategies
    expected rows = 1440

RQ2:
    Can QUBO-graph-aware variable ordering and topology-aware logical mapping
    reduce transpilation overhead relative to natural, random, and standard
    Qiskit baselines?

Important:
    This experiment does not claim quantum advantage.
    It evaluates compilation/transpilation metrics only.
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
from src.rq2_mapping_eval import (
    available_rq2_strategies,
    prepare_rq2_mapping_condition,
)
from src.qaoa_circuits import build_qaoa_p1_circuit, circuit_basic_metrics
from src.topologies import get_coupling_map
from src.transpile_eval import transpile_and_evaluate


GRAPH_METRICS_PATH = PROJECT_ROOT / "results" / "rq1_extended" / "graph_metrics.csv"

RESULTS_DIR = PROJECT_ROOT / "results" / "rq2_full"
OUTPUT_PATH = RESULTS_DIR / "rq2_mapping_metrics.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


RQ2_TOPOLOGIES = [
    "line",
    "grid_2d",
    "heavy_hex_like",
]


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)

    gamma = 0.7
    beta = 0.3
    p = 1

    optimization_level = 1
    seed_transpiler = 123
    random_seed = 123

    strategies = available_rq2_strategies()

    rows = []

    total_jobs = len(graph_df) * len(RQ2_TOPOLOGIES) * len(strategies)
    job_counter = 0

    for _, instance_row in graph_df.iterrows():
        qubo = load_qubo_json(PROJECT_ROOT / instance_row["qubo_json"])
        qubo_graph = qubo_to_interaction_graph(qubo)

        for topology_name in RQ2_TOPOLOGIES:
            coupling_map = get_coupling_map(
                topology_name=topology_name,
                n_qubits=qubo["n_variables"],
            )

            for strategy_name in strategies:
                job_counter += 1

                try:
                    condition = prepare_rq2_mapping_condition(
                        qubo=qubo,
                        qubo_graph=qubo_graph,
                        coupling_map=coupling_map,
                        strategy_name=strategy_name,
                        random_seed=random_seed,
                    )

                    relabeled_qubo = condition["relabeled_qubo"]

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
                        initial_layout=condition["initial_layout"],
                    )

                    post_metrics = result["metrics"]

                    output_row = {
                        "original_instance_name": qubo["name"],
                        "family": qubo["family"],
                        "n_variables": qubo["n_variables"],
                        "n_quadratic_terms": len(qubo["quadratic"]),
                        "qubo_json": instance_row["qubo_json"],

                        "strategy_name": strategy_name,
                        "layout_mode": condition["layout_mode"],
                        "relabeling_mode": condition["relabeling_mode"],

                        "ordering_used": json.dumps(condition["ordering_used"]),
                        "physical_ordering_used": json.dumps(
                            condition["physical_ordering_used"]
                        ),
                        "initial_layout": json.dumps(condition["initial_layout"]),

                        "p": p,
                        "gamma": gamma,
                        "beta": beta,

                        "topology": topology_name,
                        "optimization_level": optimization_level,
                        "seed_transpiler": seed_transpiler,
                        "random_seed": random_seed,

                        "pre_transpile_depth": pre_metrics["depth"],
                        "pre_transpile_gate_count": pre_metrics["gate_count"],
                        "pre_transpile_2q_count": pre_metrics["two_qubit_gate_count"],

                        "transpiled_depth": post_metrics["transpiled_depth"],
                        "transpiled_gate_count": post_metrics["transpiled_gate_count"],
                        "transpiled_2q_count": post_metrics["transpiled_2q_count"],
                        "swap_count": post_metrics["swap_count"],
                        "cx_count": post_metrics["cx_count"],
                        "transpilation_time_sec": post_metrics["transpilation_time_sec"],

                        "depth_overhead": (
                            post_metrics["transpiled_depth"] / pre_metrics["depth"]
                        ),
                        "twoq_overhead": (
                            post_metrics["transpiled_2q_count"]
                            / pre_metrics["two_qubit_gate_count"]
                            if pre_metrics["two_qubit_gate_count"] > 0
                            else None
                        ),

                        "failure_flag": False,
                        "failure_message": "",
                        "transpiled_ops_json": json.dumps(
                            post_metrics["transpiled_ops"],
                            sort_keys=True,
                        ),
                    }

                except Exception as exc:
                    output_row = {
                        "original_instance_name": instance_row["instance_name"],
                        "family": instance_row["family"],
                        "n_variables": instance_row["n_variables"],
                        "n_quadratic_terms": instance_row["n_edges"],
                        "qubo_json": instance_row["qubo_json"],

                        "strategy_name": strategy_name,
                        "layout_mode": None,
                        "relabeling_mode": None,

                        "ordering_used": None,
                        "physical_ordering_used": None,
                        "initial_layout": None,

                        "p": p,
                        "gamma": gamma,
                        "beta": beta,

                        "topology": topology_name,
                        "optimization_level": optimization_level,
                        "seed_transpiler": seed_transpiler,
                        "random_seed": random_seed,

                        "pre_transpile_depth": None,
                        "pre_transpile_gate_count": None,
                        "pre_transpile_2q_count": None,

                        "transpiled_depth": None,
                        "transpiled_gate_count": None,
                        "transpiled_2q_count": None,
                        "swap_count": None,
                        "cx_count": None,
                        "transpilation_time_sec": None,

                        "depth_overhead": None,
                        "twoq_overhead": None,

                        "failure_flag": True,
                        "failure_message": str(exc),
                        "transpiled_ops_json": None,
                    }

                rows.append(output_row)

                if job_counter % 80 == 0:
                    print(f"completed {job_counter}/{total_jobs}")

    out = pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Add natural_fixed baseline deltas within each instance/topology group.
    # ------------------------------------------------------------------
    baseline_cols = [
        "original_instance_name",
        "topology",
    ]

    natural_fixed = out[out["strategy_name"] == "natural_fixed"][
        baseline_cols
        + [
            "transpiled_depth",
            "transpiled_gate_count",
            "transpiled_2q_count",
            "swap_count",
            "depth_overhead",
            "twoq_overhead",
        ]
    ].copy()

    natural_fixed = natural_fixed.rename(
        columns={
            "transpiled_depth": "natural_fixed_transpiled_depth",
            "transpiled_gate_count": "natural_fixed_transpiled_gate_count",
            "transpiled_2q_count": "natural_fixed_transpiled_2q_count",
            "swap_count": "natural_fixed_swap_count",
            "depth_overhead": "natural_fixed_depth_overhead",
            "twoq_overhead": "natural_fixed_twoq_overhead",
        }
    )

    out = out.merge(
        natural_fixed,
        on=baseline_cols,
        how="left",
        validate="many_to_one",
    )

    out["delta_depth_vs_natural_fixed"] = (
        out["transpiled_depth"] - out["natural_fixed_transpiled_depth"]
    )
    out["delta_gate_count_vs_natural_fixed"] = (
        out["transpiled_gate_count"] - out["natural_fixed_transpiled_gate_count"]
    )
    out["delta_2q_vs_natural_fixed"] = (
        out["transpiled_2q_count"] - out["natural_fixed_transpiled_2q_count"]
    )
    out["delta_swap_vs_natural_fixed"] = (
        out["swap_count"] - out["natural_fixed_swap_count"]
    )

    out["pct_depth_change_vs_natural_fixed"] = (
        100.0
        * out["delta_depth_vs_natural_fixed"]
        / out["natural_fixed_transpiled_depth"]
    )
    out["pct_gate_count_change_vs_natural_fixed"] = (
        100.0
        * out["delta_gate_count_vs_natural_fixed"]
        / out["natural_fixed_transpiled_gate_count"]
    )
    out["pct_2q_change_vs_natural_fixed"] = (
        100.0
        * out["delta_2q_vs_natural_fixed"]
        / out["natural_fixed_transpiled_2q_count"]
    )

    out["pct_swap_change_vs_natural_fixed"] = out.apply(
        lambda row: (
            100.0
            * row["delta_swap_vs_natural_fixed"]
            / row["natural_fixed_swap_count"]
            if pd.notna(row["natural_fixed_swap_count"])
            and row["natural_fixed_swap_count"] != 0
            else None
        ),
        axis=1,
    )

    # ------------------------------------------------------------------
    # Add standard_qiskit baseline deltas within each instance/topology group.
    # ------------------------------------------------------------------
    standard = out[out["strategy_name"] == "standard_qiskit"][
        baseline_cols
        + [
            "transpiled_depth",
            "transpiled_gate_count",
            "transpiled_2q_count",
            "swap_count",
        ]
    ].copy()

    standard = standard.rename(
        columns={
            "transpiled_depth": "standard_qiskit_transpiled_depth",
            "transpiled_gate_count": "standard_qiskit_transpiled_gate_count",
            "transpiled_2q_count": "standard_qiskit_transpiled_2q_count",
            "swap_count": "standard_qiskit_swap_count",
        }
    )

    out = out.merge(
        standard,
        on=baseline_cols,
        how="left",
        validate="many_to_one",
    )

    out["delta_depth_vs_standard_qiskit"] = (
        out["transpiled_depth"] - out["standard_qiskit_transpiled_depth"]
    )
    out["delta_gate_count_vs_standard_qiskit"] = (
        out["transpiled_gate_count"] - out["standard_qiskit_transpiled_gate_count"]
    )
    out["delta_2q_vs_standard_qiskit"] = (
        out["transpiled_2q_count"] - out["standard_qiskit_transpiled_2q_count"]
    )
    out["delta_swap_vs_standard_qiskit"] = (
        out["swap_count"] - out["standard_qiskit_swap_count"]
    )

    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("Full RQ2 mapping metrics saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {out.shape}")
    print()
    print("failure counts:")
    print(out["failure_flag"].value_counts())
    print()
    print("family counts:")
    print(out["family"].value_counts())
    print()
    print("topology counts:")
    print(out["topology"].value_counts())
    print()
    print("strategy counts:")
    print(out["strategy_name"].value_counts())
    print()
    print("Mean delta vs natural_fixed by strategy:")
    print(
        out.groupby("strategy_name", as_index=False)
        .agg(
            n_rows=("original_instance_name", "count"),
            mean_delta_depth=("delta_depth_vs_natural_fixed", "mean"),
            mean_delta_gate=("delta_gate_count_vs_natural_fixed", "mean"),
            mean_delta_2q=("delta_2q_vs_natural_fixed", "mean"),
            mean_delta_swap=("delta_swap_vs_natural_fixed", "mean"),
            mean_pct_depth=("pct_depth_change_vs_natural_fixed", "mean"),
            mean_pct_2q=("pct_2q_change_vs_natural_fixed", "mean"),
            mean_pct_swap=("pct_swap_change_vs_natural_fixed", "mean"),
        )
        .round(3)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
