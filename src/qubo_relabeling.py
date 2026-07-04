"""
QUBO variable relabeling utilities for RQ2.

RQ2 compares variable ordering strategies.

To make an ordering affect the generated QAOA circuit, we relabel QUBO
variables according to the ordering.

Example:
    ordering = [5, 2, 0]

means:
    new variable 0 represents old variable 5
    new variable 1 represents old variable 2
    new variable 2 represents old variable 0

This changes how QUBO interactions are placed onto circuit qubits before
transpilation.
"""

from __future__ import annotations

from typing import Dict, Any, List, Tuple


def relabel_qubo_by_ordering(
    qubo: Dict[str, Any],
    ordering: List[int],
    new_name_suffix: str | None = None,
) -> Dict[str, Any]:
    """
    Relabel QUBO variables according to a given ordering.

    Parameters
    ----------
    qubo:
        Original QUBO dictionary.

    ordering:
        List of old variable indices in the desired new order.

        If ordering = [5, 2, 0], then:
            old 5 -> new 0
            old 2 -> new 1
            old 0 -> new 2

    new_name_suffix:
        Optional suffix added to the QUBO name.

    Returns
    -------
    relabeled_qubo:
        QUBO dictionary with variables relabeled to 0..n-1.
    """
    n = int(qubo["n_variables"])

    if len(ordering) != n:
        raise ValueError("Ordering length must match number of QUBO variables.")

    if set(ordering) != set(range(n)):
        raise ValueError("Ordering must be a permutation of 0..n-1.")

    old_to_new = {
        int(old_var): int(new_pos)
        for new_pos, old_var in enumerate(ordering)
    }

    new_to_old = {
        int(new_pos): int(old_var)
        for new_pos, old_var in enumerate(ordering)
    }

    # Relabel linear terms
    new_linear = {}

    for old_i, value in qubo["linear"].items():
        new_i = old_to_new[int(old_i)]
        new_linear[new_i] = float(value)

    # Relabel quadratic terms
    new_quadratic: Dict[Tuple[int, int], float] = {}

    for (old_i, old_j), value in qubo["quadratic"].items():
        new_i = old_to_new[int(old_i)]
        new_j = old_to_new[int(old_j)]

        if new_i == new_j:
            raise ValueError("Relabeling produced invalid self-loop.")

        a, b = sorted((new_i, new_j))
        new_quadratic[(a, b)] = new_quadratic.get((a, b), 0.0) + float(value)

    suffix = "" if new_name_suffix is None else f"_{new_name_suffix}"

    relabeled = {
        "name": f"{qubo['name']}{suffix}",
        "family": qubo["family"],
        "n_variables": n,
        "linear": new_linear,
        "quadratic": new_quadratic,
        "constant": float(qubo["constant"]),
        "metadata": dict(qubo.get("metadata", {})),
    }

    relabeled["metadata"]["relabeling_ordering"] = [int(x) for x in ordering]
    relabeled["metadata"]["old_to_new"] = old_to_new
    relabeled["metadata"]["new_to_old"] = new_to_old

    return relabeled


def qubo_energy(qubo: Dict[str, Any], bitstring: List[int]) -> float:
    """
    Compute QUBO energy for a binary bitstring.

    This is used to verify that relabeling preserves the objective.
    """
    n = int(qubo["n_variables"])

    if len(bitstring) != n:
        raise ValueError("Bitstring length must match number of QUBO variables.")

    x = [int(v) for v in bitstring]

    energy = float(qubo.get("constant", 0.0))

    for i, value in qubo["linear"].items():
        energy += float(value) * x[int(i)]

    for (i, j), value in qubo["quadratic"].items():
        energy += float(value) * x[int(i)] * x[int(j)]

    return float(energy)


def map_old_bitstring_to_new(
    old_bitstring: List[int],
    ordering: List[int],
) -> List[int]:
    """
    Convert an old-variable bitstring to a new-variable bitstring.

    If new variable position k represents old variable ordering[k], then:

        new_x[k] = old_x[ordering[k]]
    """
    return [
        int(old_bitstring[int(old_var)])
        for old_var in ordering
    ]
