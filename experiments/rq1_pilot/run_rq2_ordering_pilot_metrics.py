"""
Run RQ2 ordering pilot experiment.

This script evaluates whether QUBO-graph-aware variable ordering reduces
topology-aware transpilation overhead under fixed initial layout.

Input:
    results/rq1_extended/graph_metrics.csv

Output:
    results/rq2_pilot/rq2_ordering_pilot_metrics.csv

Pilot scope:
    families: maxcut, assignment, scheduling_toy
    sizes: 16, 24 variables
    topologies: line, grid_2d, heavy_hex_like
    strategies: natural, random, degree_desc, weighted_degree_desc

Layout mode:
    fixed_identity_after_relabeling

Meaning:
    First relabel QUBO variables according to the ordering strategy.
    Then impose initial_layout = [0, 1, ..., n-1].
    Therefore, ordering affects logical-to-physical placement.
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
OUTPUT_PATH = RESULTS_DIR / "rq2_ordering_pilot_metrics.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


PILOT_SIZES = [16, 24]
PILOT_TOPOLOGIES = ["line", "grid_2d", "heavy_hex_like"]


def main() -> None:
    graph_df = pd.read_csv(GRAPH_METRICS_PATH)

    pilot_df = graph_df[
        graph_df["n_variables"].isin(PILOT_SIZES)
    ].copy()

    if len(pilot_df) == 0:
        raise ValueError("No pilot instances found.")

    gamma = 0.7
    beta = 0.3
    p = 1
    optimization_level = 1
    seed_transpiler = 123
    random_ordering_seed = 123

    rows = []

    total_jobs = (
        len(pilot_df)
        * len(PILOT_TOPOLOGIES)
        * len(available_ordering_strategies())
    )

    job_counter = 0

    for _, instance_row in pilot_df.iterrows():
        original_qubo = load_qubo_json(PROJECT_ROOT / instance_row["qubo_json"])
        original_graph = qubo_to_interaction_graph(original_qubo)

        for topology_name in PILOT_TOPOLOGIES:
            for strategy in available_ordering_strategies():
                job_counter += 1

                ordering = get_variable_ordering(
                    original_graph,
                    strategy=strategy,
                    seed=random_ordering_seed,
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

                initial_layout = list(range(circuit.num_qubits))

                try:
                    result = transpile_and_evaluate(
                        circuit=circuit,
                        coupling_map=coupling_map,
                        topology_name=topology_name,
                        optimization_level=optimization_level,
                        seed_transpiler=seed_transpiler,
                        initial_layout=initial_layout,
                    )

                    post_metrics = result["metrics"]

                    output_row = {
                        "original_instance_name": original_qubo["name"],
                        "relabeled_instance_name": relabeled_qubo["name"],
                        "family": original_qubo["family"],
                        "n_variables": original_qubo["n_variables"],
                        "n_quadratic_terms": len(original_qubo["quadratic"]),
                        "qubo_json": instance_row["qubo_json"],

                        "ordering_strategy": strategy,
                        "ordering": json.dumps(ordering),
                        "random_ordering_seed": random_ordering_seed,

                        "layout_mode": "fixed_identity_after_relabeling",
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

                        "failure_flag": False,
                        "failure_message": "",
                        "transpiled_ops_json": json.dumps(
                            post_metrics["transpiled_ops"],
                            sort_keys=True,
                        ),
                    }

                except Exception as exc:
                    output_row = {
                        "original_instance_name": original_qubo["name"],
                        "relabeled_instance_name": relabeled_qubo["name"],
                        "family": original_qubo["family"],
                        "n_variables": original_qubo["n_variables"],
                        "n_quadratic_terms": len(original_qubo["quadratic"]),
                        "qubo_json": instance_row["qubo_json"],

                        "ordering_strategy": strategy,
                        "ordering": json.dumps(ordering),
                        "random_ordering_seed": random_ordering_seed,

                        "layout_mode": "fixed_identity_after_relabeling",
                        "initial_layout": json.dumps(list(range(original_qubo["n_variables"]))),

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

                rows.append(output_row)

                if job_counter % 24 == 0:
                    print(f"completed {job_counter}/{total_jobs}")

    out = pd.DataFrame(rows)

    # Add natural-baseline deltas within each instance/topology group.
    baseline_cols = [
        "original_instance_name",
        "topology",
    ]

    natural = out[out["ordering_strategy"] == "natural"][
        baseline_cols
        + [
            "transpiled_depth",
            "transpiled_2q_count",
            "swap_count",
            "depth_overhead",
            "twoq_overhead",
        ]
    ].copy()

    natural = natural.rename(
        columns={
            "transpiled_depth": "natural_transpiled_depth",
            "transpiled_2q_count": "natural_transpiled_2q_count",
            "swap_count": "natural_swap_count",
            "depth_overhead": "natural_depth_overhead",
            "twoq_overhead": "natural_twoq_overhead",
        }
    )

    out = out.merge(
        natural,
        on=baseline_cols,
        how="left",
        validate="many_to_one",
    )

    out["delta_depth_vs_natural"] = (
        out["transpiled_depth"] - out["natural_transpiled_depth"]
    )
    out["delta_2q_vs_natural"] = (
        out["transpiled_2q_count"] - out["natural_transpiled_2q_count"]
    )
    out["delta_swap_vs_natural"] = (
        out["swap_count"] - out["natural_swap_count"]
    )

    out["pct_depth_change_vs_natural"] = (
        100.0 * out["delta_depth_vs_natural"] / out["natural_transpiled_depth"]
    )

    out["pct_2q_change_vs_natural"] = (
        100.0 * out["delta_2q_vs_natural"] / out["natural_transpiled_2q_count"]
    )

    out["pct_swap_change_vs_natural"] = out.apply(
        lambda row: (
            100.0 * row["delta_swap_vs_natural"] / row["natural_swap_count"]
            if row["natural_swap_count"] not in [0, None] and pd.notna(row["natural_swap_count"])
            else None
        ),
        axis=1,
    )

    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ2 ordering pilot metrics saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {out.shape}")
    print()
    print("family counts:")
    print(out["family"].value_counts())
    print()
    print("topology counts:")
    print(out["topology"].value_counts())
    print()
    print("ordering counts:")
    print(out["ordering_strategy"].value_counts())
    print()
    print("failure counts:")
    print(out["failure_flag"].value_counts())
    print()
    print("Mean delta vs natural by strategy:")
    print(
        out.groupby("ordering_strategy", as_index=False)
        .agg(
            n_rows=("original_instance_name", "count"),
            mean_delta_depth=("delta_depth_vs_natural", "mean"),
            mean_delta_2q=("delta_2q_vs_natural", "mean"),
            mean_delta_swap=("delta_swap_vs_natural", "mean"),
            mean_pct_depth_change=("pct_depth_change_vs_natural", "mean"),
            mean_pct_2q_change=("pct_2q_change_vs_natural", "mean"),
            mean_pct_swap_change=("pct_swap_change_vs_natural", "mean"),
        )
        .round(3)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
