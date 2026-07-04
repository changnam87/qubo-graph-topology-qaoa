"""
RQ2 final-scope dry run.

This script tests the final RQ2 strategy set on a very small subset before
running the full RQ2 experiment.

Input:
    results/rq1_extended/graph_metrics.csv

Output:
    results/rq2_pilot/rq2_final_scope_dry_run.csv

Scope:
    3 instances
    2 topologies
    8 RQ2 strategies
    expected rows = 48
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

RESULTS_DIR = PROJECT_ROOT / "results" / "rq2_pilot"
OUTPUT_PATH = RESULTS_DIR / "rq2_final_scope_dry_run.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


DRY_RUN_TOPOLOGIES = [
    "line",
    "grid_2d",
]


def select_dry_run_instances(graph_df: pd.DataFrame) -> pd.DataFrame:
    """
    Select one instance from each family at n_variables = 16.
    """
    rows = []

    for family in ["maxcut", "assignment", "scheduling_toy"]:
        sub = graph_df[
            (graph_df["family"] == family)
            & (graph_df["n_variables"] == 16)
        ].copy()

        if len(sub) == 0:
            raise ValueError(f"No dry-run instance found for family={family}")

        rows.append(sub.iloc[0])

    return pd.DataFrame(rows)


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)
    dry_df = select_dry_run_instances(graph_df)

    gamma = 0.7
    beta = 0.3
    p = 1
    optimization_level = 1
    seed_transpiler = 123
    random_seed = 123

    rows = []

    total_jobs = (
        len(dry_df)
        * len(DRY_RUN_TOPOLOGIES)
        * len(available_rq2_strategies())
    )

    job_counter = 0

    for _, instance_row in dry_df.iterrows():
        qubo = load_qubo_json(PROJECT_ROOT / instance_row["qubo_json"])
        qubo_graph = qubo_to_interaction_graph(qubo)

        for topology_name in DRY_RUN_TOPOLOGIES:
            coupling_map = get_coupling_map(
                topology_name=topology_name,
                n_qubits=qubo["n_variables"],
            )

            for strategy_name in available_rq2_strategies():
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

                    row = {
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
                    row = {
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

                rows.append(row)

                if job_counter % 16 == 0:
                    print(f"completed {job_counter}/{total_jobs}")

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ2 final-scope dry run saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {out.shape}")
    print()
    print("failure counts:")
    print(out["failure_flag"].value_counts())
    print()
    print("strategy counts:")
    print(out["strategy_name"].value_counts())
    print()
    print("topology counts:")
    print(out["topology"].value_counts())
    print()
    print("mean metrics by strategy:")
    print(
        out.groupby("strategy_name", as_index=False)
        .agg(
            n_rows=("original_instance_name", "count"),
            mean_depth=("transpiled_depth", "mean"),
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
