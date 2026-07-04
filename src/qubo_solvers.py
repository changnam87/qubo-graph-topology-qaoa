"""
Classical QUBO solver utilities for RQ3.

These utilities are used only as reference tools for evaluating
sub-QUBO solution-quality preservation.

They are not used to claim classical or quantum superiority.

Functions:
    qubo_energy
    brute_force_solve_qubo
    greedy_local_search_qubo
"""

from __future__ import annotations

from typing import Dict, Any, List
import itertools
import numpy as np


def qubo_energy(
    qubo: Dict[str, Any],
    bitstring: List[int],
) -> float:
    """
    Compute QUBO energy for a binary bitstring.

    QUBO form:
        E(x) = constant + sum_i q_i x_i + sum_{i<j} q_ij x_i x_j

    Lower energy is better.
    """
    n = int(qubo["n_variables"])

    if len(bitstring) != n:
        raise ValueError("Bitstring length must match number of QUBO variables.")

    x = [int(v) for v in bitstring]

    energy = float(qubo.get("constant", 0.0))

    for i, value in qubo["linear"].items():
        energy += float(value) * x[int(i)]

    for key, value in qubo["quadratic"].items():
        if isinstance(key, tuple):
            i, j = key
        else:
            i, j = str(key).split(",")

        energy += float(value) * x[int(i)] * x[int(j)]

    return float(energy)


def brute_force_solve_qubo(
    qubo: Dict[str, Any],
    max_variables: int = 20,
) -> Dict[str, Any]:
    """
    Exact brute-force QUBO solver.

    This is intended for small sub-QUBOs only.

    Parameters
    ----------
    qubo:
        QUBO dictionary.

    max_variables:
        Safety limit. If n_variables exceeds this limit, raise ValueError.

    Returns
    -------
    result:
        Dictionary with best_bitstring, best_energy, n_evaluated.
    """
    n = int(qubo["n_variables"])

    if n > max_variables:
        raise ValueError(
            f"Brute force refused: n_variables={n} exceeds max_variables={max_variables}."
        )

    best_energy = None
    best_bitstring = None
    n_evaluated = 0

    for bits in itertools.product([0, 1], repeat=n):
        bits = list(bits)
        energy = qubo_energy(qubo, bits)
        n_evaluated += 1

        if best_energy is None or energy < best_energy:
            best_energy = energy
            best_bitstring = bits

    return {
        "method": "brute_force",
        "best_bitstring": best_bitstring,
        "best_energy": float(best_energy),
        "n_evaluated": int(n_evaluated),
        "n_variables": n,
    }


def random_bitstring(
    n_variables: int,
    rng: np.random.Generator,
) -> List[int]:
    """
    Generate a random binary bitstring.
    """
    return rng.integers(0, 2, size=n_variables).astype(int).tolist()


def greedy_local_search_qubo(
    qubo: Dict[str, Any],
    n_restarts: int = 100,
    max_passes: int = 100,
    seed: int = 123,
) -> Dict[str, Any]:
    """
    Simple greedy bit-flip local search for QUBO minimization.

    Algorithm:
        1. Start from a random bitstring.
        2. Try flipping each bit.
        3. Accept the flip if it improves energy.
        4. Repeat until no improving flip is found or max_passes is reached.
        5. Repeat for n_restarts.

    This is a reference heuristic for original QUBOs that are too large
    for brute force.
    """
    n = int(qubo["n_variables"])
    rng = np.random.default_rng(seed)

    global_best_bits = None
    global_best_energy = None

    total_energy_evaluations = 0

    for restart in range(n_restarts):
        current_bits = random_bitstring(n, rng)
        current_energy = qubo_energy(qubo, current_bits)
        total_energy_evaluations += 1

        improved = True
        passes = 0

        while improved and passes < max_passes:
            improved = False
            passes += 1

            for idx in range(n):
                candidate_bits = list(current_bits)
                candidate_bits[idx] = 1 - candidate_bits[idx]

                candidate_energy = qubo_energy(qubo, candidate_bits)
                total_energy_evaluations += 1

                if candidate_energy < current_energy:
                    current_bits = candidate_bits
                    current_energy = candidate_energy
                    improved = True

        if global_best_energy is None or current_energy < global_best_energy:
            global_best_energy = current_energy
            global_best_bits = current_bits

    return {
        "method": "greedy_local_search",
        "best_bitstring": global_best_bits,
        "best_energy": float(global_best_energy),
        "n_restarts": int(n_restarts),
        "max_passes": int(max_passes),
        "n_energy_evaluations": int(total_energy_evaluations),
        "n_variables": n,
        "seed": int(seed),
    }


def evaluate_solution_on_qubo(
    qubo: Dict[str, Any],
    bitstring: List[int],
) -> Dict[str, Any]:
    """
    Evaluate a given bitstring on a QUBO.
    """
    return {
        "n_variables": int(qubo["n_variables"]),
        "energy": qubo_energy(qubo, bitstring),
    }


def lift_subqubo_solution_to_original(
    subqubo: Dict[str, Any],
    sub_bitstring: List[int],
    fill_value: int = 0,
) -> List[int]:
    """
    Lift a sub-QUBO solution back to the original QUBO variable space.

    The sub-QUBO metadata must contain:
        subqubo_new_to_old
        subqubo_original_n_variables

    Parameters
    ----------
    subqubo:
        Sub-QUBO dictionary produced by extract_subqubo.

    sub_bitstring:
        Binary solution for the sub-QUBO.

    fill_value:
        Value assigned to original variables not included in the sub-QUBO.
        Current default is 0.

    Returns
    -------
    original_bitstring:
        Binary bitstring with length equal to original_n_variables.
    """
    if fill_value not in [0, 1]:
        raise ValueError("fill_value must be 0 or 1.")

    metadata = subqubo.get("metadata", {})

    if "subqubo_new_to_old" not in metadata:
        raise ValueError("Missing metadata: subqubo_new_to_old")

    if "subqubo_original_n_variables" not in metadata:
        raise ValueError("Missing metadata: subqubo_original_n_variables")

    original_n = int(metadata["subqubo_original_n_variables"])
    new_to_old = metadata["subqubo_new_to_old"]

    if len(sub_bitstring) != int(subqubo["n_variables"]):
        raise ValueError("sub_bitstring length must match sub-QUBO n_variables.")

    original_bitstring = [int(fill_value)] * original_n

    for new_idx, old_idx in new_to_old.items():
        original_bitstring[int(old_idx)] = int(sub_bitstring[int(new_idx)])

    return original_bitstring


def solution_hamming_weight(bitstring: List[int]) -> int:
    """
    Count number of selected/active binary variables.
    """
    return int(sum(int(x) for x in bitstring))
