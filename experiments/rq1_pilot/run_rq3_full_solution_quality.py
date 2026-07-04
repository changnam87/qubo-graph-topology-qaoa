"""
RQ3 full sub-QUBO solution-quality preservation experiment.

Input:
    results/rq3_full/subqubo_extraction_metrics.csv

Output:
    results/rq3_full/subqubo_solution_quality_metrics.csv

Purpose:
    Evaluate how well exact sub-QUBO solutions preserve original-QUBO
    solution quality after being lifted back to the original variable space.

Important:
    Classical solvers are used only as reference tools.
    No classical superiority, quantum superiority, or QAOA superiority claim is made.
"""

from __future__ import annotations

from pathlib import Path
import sys
import json

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


from src.qubo_io import load_qubo_json
from src.qubo_solvers import (
    brute_force_solve_qubo,
    greedy_local_search_qubo,
    lift_subqubo_solution_to_original,
    qubo_energy,
    solution_hamming_weight,
)


EXTRACTION_PATH = PROJECT_ROOT / "results" / "rq3_full" / "subqubo_extraction_metrics.csv"

RESULTS_DIR = PROJECT_ROOT / "results" / "rq3_full"
OUTPUT_PATH = RESULTS_DIR / "subqubo_solution_quality_metrics.csv"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)


def main() -> None:
    extraction_df = pd.read_csv(EXTRACTION_PATH)

    rows = []

    # Cache original-QUBO reference solutions so each original is solved once.
    original_solution_cache = {}

    n_restarts = 200
    max_passes = 100
    local_search_seed = 123

    total = len(extraction_df)

    for idx, row in extraction_df.iterrows():
        original_name = row["original_instance_name"]

        original_qubo = load_qubo_json(PROJECT_ROOT / row["original_qubo_json"])
        subqubo = load_qubo_json(PROJECT_ROOT / row["subqubo_json"])

        if original_name not in original_solution_cache:
            ref = greedy_local_search_qubo(
                original_qubo,
                n_restarts=n_restarts,
                max_passes=max_passes,
                seed=local_search_seed,
            )
            original_solution_cache[original_name] = ref

        original_ref = original_solution_cache[original_name]

        sub_exact = brute_force_solve_qubo(
            subqubo,
            max_variables=20,
        )

        lifted_bits = lift_subqubo_solution_to_original(
            subqubo=subqubo,
            sub_bitstring=sub_exact["best_bitstring"],
            fill_value=0,
        )

        lifted_original_energy = qubo_energy(
            original_qubo,
            lifted_bits,
        )

        reference_energy = original_ref["best_energy"]

        # Lower QUBO energy is better.
        energy_gap_vs_reference = lifted_original_energy - reference_energy

        normalized_energy_gap = (
            energy_gap_vs_reference / (abs(reference_energy) + 1e-9)
        )

        row_out = {
            "original_instance_name": row["original_instance_name"],
            "original_family": row["original_family"],
            "original_n_variables": row["original_n_variables"],
            "original_n_edges": row["original_n_edges"],
            "original_qubo_json": row["original_qubo_json"],

            "subqubo_name": row["subqubo_name"],
            "subqubo_json": row["subqubo_json"],
            "subqubo_n_variables": row["subqubo_n_variables"],
            "subqubo_n_edges": row["subqubo_n_edges"],

            "extraction_strategy": row["extraction_strategy"],
            "k_variables": row["k_variables"],

            "variable_preservation_ratio": row["variable_preservation_ratio"],
            "edge_preservation_ratio": row["edge_preservation_ratio"],
            "weighted_edge_preservation_ratio": row["weighted_edge_preservation_ratio"],

            "original_reference_method": original_ref["method"],
            "original_reference_energy": reference_energy,
            "original_reference_hamming_weight": solution_hamming_weight(
                original_ref["best_bitstring"]
            ),
            "original_reference_n_restarts": original_ref["n_restarts"],
            "original_reference_max_passes": original_ref["max_passes"],
            "original_reference_energy_evaluations": original_ref["n_energy_evaluations"],

            "subqubo_solver_method": sub_exact["method"],
            "subqubo_exact_energy": sub_exact["best_energy"],
            "subqubo_exact_hamming_weight": solution_hamming_weight(
                sub_exact["best_bitstring"]
            ),
            "subqubo_n_evaluated": sub_exact["n_evaluated"],

            "lift_fill_value": 0,
            "lifted_original_energy": lifted_original_energy,
            "lifted_hamming_weight": solution_hamming_weight(lifted_bits),

            "energy_gap_vs_reference": energy_gap_vs_reference,
            "normalized_energy_gap_vs_reference": normalized_energy_gap,

            "subqubo_best_bitstring": json.dumps(sub_exact["best_bitstring"]),
            "lifted_bitstring": json.dumps(lifted_bits),
        }

        rows.append(row_out)

        if (idx + 1) % 24 == 0:
            print(f"completed {idx + 1}/{total}")

    out = pd.DataFrame(rows)
    out.to_csv(OUTPUT_PATH, index=False)

    print("=" * 80)
    print("RQ3 full sub-QUBO solution-quality metrics saved")
    print("=" * 80)
    print(f"output: {OUTPUT_PATH}")
    print(f"shape: {out.shape}")
    print()
    print("original reference solutions computed:", len(original_solution_cache))
    print()
    print("strategy counts:")
    print(out["extraction_strategy"].value_counts())
    print()
    print("k counts:")
    print(out["k_variables"].value_counts().sort_index())
    print()
    print("summary by strategy:")
    print(
        out.groupby("extraction_strategy", as_index=False)
        .agg(
            n_rows=("subqubo_name", "count"),
            mean_weighted_edge_preservation=("weighted_edge_preservation_ratio", "mean"),
            mean_energy_gap=("energy_gap_vs_reference", "mean"),
            median_energy_gap=("energy_gap_vs_reference", "median"),
            mean_normalized_gap=("normalized_energy_gap_vs_reference", "mean"),
            median_normalized_gap=("normalized_energy_gap_vs_reference", "median"),
            mean_lifted_hamming_weight=("lifted_hamming_weight", "mean"),
        )
        .round(4)
        .to_string(index=False)
    )


if __name__ == "__main__":
    main()
