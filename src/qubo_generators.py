"""
QUBO benchmark generators for the RQ1 pilot experiment.

This module creates small QUBO instances for:
1. MaxCut-style QUBOs
2. Assignment-style QUBOs

QUBO convention:

    minimize  sum_i h_i x_i + sum_{i<j} q_ij x_i x_j + constant

where x_i is binary, x_i in {0, 1}.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple, Any
import numpy as np


LinearTerms = Dict[int, float]
QuadraticTerms = Dict[Tuple[int, int], float]


@dataclass
class QUBOInstance:
    """Simple container for one QUBO instance."""
    name: str
    family: str
    n_variables: int
    linear: LinearTerms
    quadratic: QuadraticTerms
    constant: float
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert the QUBO instance into a plain dictionary."""
        return {
            "name": self.name,
            "family": self.family,
            "n_variables": self.n_variables,
            "linear": self.linear,
            "quadratic": self.quadratic,
            "constant": self.constant,
            "metadata": self.metadata,
        }


def _clean_quadratic_terms(
    quadratic: QuadraticTerms,
    zero_tol: float = 1e-12,
) -> QuadraticTerms:
    """
    Standardize quadratic keys as (i, j) with i < j.
    Remove near-zero coefficients.
    """
    cleaned: QuadraticTerms = {}

    for (i, j), value in quadratic.items():
        if i == j:
            raise ValueError("Quadratic terms must not contain self-loops.")

        if abs(value) <= zero_tol:
            continue

        a, b = sorted((int(i), int(j)))
        cleaned[(a, b)] = cleaned.get((a, b), 0.0) + float(value)

    return {
        key: value
        for key, value in cleaned.items()
        if abs(value) > zero_tol
    }


def generate_maxcut_qubo(
    n_variables: int,
    edge_probability: float,
    seed: int,
    weight_low: int = 1,
    weight_high: int = 10,
) -> QUBOInstance:
    """
    Generate a MaxCut-style QUBO.

    For an edge (i, j) with weight w, MaxCut maximizes:

        w * (x_i + x_j - 2 x_i x_j)

    Since our QUBO convention is minimization, we minimize the negative:

        -w x_i - w x_j + 2w x_i x_j
    """
    if n_variables < 2:
        raise ValueError("MaxCut QUBO needs at least two variables.")

    rng = np.random.default_rng(seed)

    linear: LinearTerms = {i: 0.0 for i in range(n_variables)}
    quadratic: QuadraticTerms = {}

    for i in range(n_variables):
        for j in range(i + 1, n_variables):
            if rng.random() < edge_probability:
                w = float(rng.integers(weight_low, weight_high + 1))

                linear[i] += -w
                linear[j] += -w
                quadratic[(i, j)] = quadratic.get((i, j), 0.0) + 2.0 * w

    quadratic = _clean_quadratic_terms(quadratic)

    name = f"maxcut_n{n_variables}_p{edge_probability:.2f}_seed{seed}"

    return QUBOInstance(
        name=name,
        family="maxcut",
        n_variables=n_variables,
        linear=linear,
        quadratic=quadratic,
        constant=0.0,
        metadata={
            "edge_probability": edge_probability,
            "seed": seed,
            "weight_low": weight_low,
            "weight_high": weight_high,
        },
    )


def generate_assignment_qubo(
    n_items: int,
    n_bins: int,
    seed: int,
    penalty: float = 10.0,
    cost_low: int = 1,
    cost_high: int = 10,
) -> QUBOInstance:
    """
    Generate an assignment-style QUBO.

    Each item must be assigned to exactly one bin.

    Variable:

        x_{i,b} = 1 if item i is assigned to bin b

    Constraint:

        sum_b x_{i,b} = 1

    Penalty:

        penalty * (sum_b x_{i,b} - 1)^2
    """
    if n_items < 1:
        raise ValueError("n_items must be positive.")
    if n_bins < 2:
        raise ValueError("n_bins must be at least two.")

    rng = np.random.default_rng(seed)

    n_variables = n_items * n_bins

    def var_index(item: int, bin_id: int) -> int:
        return item * n_bins + bin_id

    linear: LinearTerms = {i: 0.0 for i in range(n_variables)}
    quadratic: QuadraticTerms = {}
    constant = 0.0

    costs = rng.integers(cost_low, cost_high + 1, size=(n_items, n_bins))

    for item in range(n_items):
        constant += penalty

        for b in range(n_bins):
            idx = var_index(item, b)

            linear[idx] += float(costs[item, b])
            linear[idx] += -penalty

        for b1 in range(n_bins):
            for b2 in range(b1 + 1, n_bins):
                idx1 = var_index(item, b1)
                idx2 = var_index(item, b2)

                quadratic[(idx1, idx2)] = quadratic.get((idx1, idx2), 0.0) + 2.0 * penalty

    quadratic = _clean_quadratic_terms(quadratic)

    name = f"assignment_items{n_items}_bins{n_bins}_seed{seed}"

    return QUBOInstance(
        name=name,
        family="assignment",
        n_variables=n_variables,
        linear=linear,
        quadratic=quadratic,
        constant=float(constant),
        metadata={
            "n_items": n_items,
            "n_bins": n_bins,
            "seed": seed,
            "penalty": penalty,
            "cost_low": cost_low,
            "cost_high": cost_high,
            "cost_matrix": costs.tolist(),
        },
    )


def generate_scheduling_toy_qubo(
    n_operations: int,
    n_machines: int,
    seed: int,
    assignment_penalty: float = 10.0,
    conflict_penalty: float = 6.0,
    cost_low: int = 1,
    cost_high: int = 10,
    conflict_probability: float = 0.25,
) -> QUBOInstance:
    """
    Generate a scheduling-derived toy QUBO.

    This is a lightweight industrial-style QUBO for RQ1 graph-structure analysis.

    Binary variable:

        x_{o,m} = 1 if operation o is assigned to machine m

    Constraint 1: each operation must be assigned to exactly one machine.

        sum_m x_{o,m} = 1

    Penalty:

        assignment_penalty * (sum_m x_{o,m} - 1)^2

    Constraint 2: selected operation pairs may conflict if assigned to the same machine.

        x_{o1,m} + x_{o2,m} <= 1 for conflict pair (o1, o2)

    Penalty approximation:

        conflict_penalty * x_{o1,m} x_{o2,m}

    This produces a QUBO interaction graph with both:
        - within-operation assignment cliques
        - cross-operation conflict edges

    The purpose is not to model full job-shop scheduling.
    The purpose is to add a scheduling-derived QUBO family for RQ1 circuit-complexity analysis.
    """
    if n_operations < 2:
        raise ValueError("n_operations must be at least 2.")

    if n_machines < 2:
        raise ValueError("n_machines must be at least 2.")

    if not (0.0 <= conflict_probability <= 1.0):
        raise ValueError("conflict_probability must be between 0 and 1.")

    rng = np.random.default_rng(seed)

    n_variables = n_operations * n_machines

    def var_index(operation: int, machine: int) -> int:
        return operation * n_machines + machine

    linear: LinearTerms = {i: 0.0 for i in range(n_variables)}
    quadratic: QuadraticTerms = {}
    constant = 0.0

    processing_costs = rng.integers(
        cost_low,
        cost_high + 1,
        size=(n_operations, n_machines),
    )

    # ------------------------------------------------------------------
    # 1. Operation-to-machine assignment cost and exactly-one penalty
    # ------------------------------------------------------------------
    for operation in range(n_operations):
        constant += assignment_penalty

        for machine in range(n_machines):
            idx = var_index(operation, machine)

            # Linear processing/assignment cost
            linear[idx] += float(processing_costs[operation, machine])

            # Linear part of assignment penalty
            linear[idx] += -assignment_penalty

        # Quadratic part of exactly-one assignment penalty
        for m1 in range(n_machines):
            for m2 in range(m1 + 1, n_machines):
                idx1 = var_index(operation, m1)
                idx2 = var_index(operation, m2)

                quadratic[(idx1, idx2)] = (
                    quadratic.get((idx1, idx2), 0.0)
                    + 2.0 * assignment_penalty
                )

    # ------------------------------------------------------------------
    # 2. Cross-operation same-machine conflict penalties
    # ------------------------------------------------------------------
    conflict_pairs = []

    for o1 in range(n_operations):
        for o2 in range(o1 + 1, n_operations):
            if rng.random() < conflict_probability:
                conflict_pairs.append((o1, o2))

                for machine in range(n_machines):
                    idx1 = var_index(o1, machine)
                    idx2 = var_index(o2, machine)

                    a, b = sorted((idx1, idx2))
                    quadratic[(a, b)] = (
                        quadratic.get((a, b), 0.0)
                        + conflict_penalty
                    )

    quadratic = _clean_quadratic_terms(quadratic)

    name = (
        f"scheduling_ops{n_operations}_machines{n_machines}"
        f"_conf{conflict_probability:.2f}_seed{seed}"
    )

    return QUBOInstance(
        name=name,
        family="scheduling_toy",
        n_variables=n_variables,
        linear=linear,
        quadratic=quadratic,
        constant=float(constant),
        metadata={
            "n_operations": n_operations,
            "n_machines": n_machines,
            "seed": seed,
            "assignment_penalty": assignment_penalty,
            "conflict_penalty": conflict_penalty,
            "cost_low": cost_low,
            "cost_high": cost_high,
            "conflict_probability": conflict_probability,
            "processing_costs": processing_costs.tolist(),
            "conflict_pairs": conflict_pairs,
        },
    )
