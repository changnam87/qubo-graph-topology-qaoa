"""
Sub-QUBO extraction utilities for RQ3.

RQ3 asks how sub-QUBO extraction strategies trade off:

1. interaction preservation
2. feasibility preservation
3. classical solution-quality preservation
4. QAOA circuit executability

This first version focuses only on extracting sub-QUBOs and computing
basic interaction-preservation metrics.

No solver or QAOA transpilation is used in this step.
"""

from __future__ import annotations

from typing import Dict, Any, List, Set, Tuple
import numpy as np
import networkx as nx


def _weighted_degree(graph: nx.Graph, node: int) -> float:
    """
    Weighted degree based on absolute interaction weights.
    """
    total = 0.0

    for _, _, data in graph.edges(node, data=True):
        total += abs(float(data.get("weight", 1.0)))

    return total


def select_subqubo_variables(
    qubo_graph: nx.Graph,
    k_variables: int,
    strategy: str,
    seed: int = 123,
) -> List[int]:
    """
    Select original QUBO variables to keep in the sub-QUBO.

    Parameters
    ----------
    qubo_graph:
        Original QUBO interaction graph.

    k_variables:
        Number of variables to keep.

    strategy:
        One of:
            top_weight_edges
            high_degree_nodes
            weighted_degree_nodes
            random_nodes

    seed:
        Random seed for random_nodes.

    Returns
    -------
    selected_variables:
        Sorted list of original variable indices selected for the sub-QUBO.
    """
    n = qubo_graph.number_of_nodes()

    if k_variables <= 0:
        raise ValueError("k_variables must be positive.")

    if k_variables > n:
        raise ValueError("k_variables cannot exceed number of graph nodes.")

    nodes = sorted(int(node) for node in qubo_graph.nodes())

    if strategy == "random_nodes":
        rng = np.random.default_rng(seed)
        selected = rng.choice(nodes, size=k_variables, replace=False)
        return sorted(int(x) for x in selected)

    if strategy == "high_degree_nodes":
        ranked = sorted(
            nodes,
            key=lambda node: (-qubo_graph.degree[node], node),
        )
        return sorted(ranked[:k_variables])

    if strategy == "weighted_degree_nodes":
        ranked = sorted(
            nodes,
            key=lambda node: (-_weighted_degree(qubo_graph, node), node),
        )
        return sorted(ranked[:k_variables])

    if strategy == "top_weight_edges":
        selected_set: Set[int] = set()

        edges = []

        for u, v, data in qubo_graph.edges(data=True):
            weight = abs(float(data.get("weight", 1.0)))
            edges.append((weight, int(u), int(v)))

        edges = sorted(
            edges,
            key=lambda item: (-item[0], item[1], item[2]),
        )

        for _, u, v in edges:
            if len(selected_set) >= k_variables:
                break

            if len(selected_set) < k_variables:
                selected_set.add(u)

            if len(selected_set) < k_variables:
                selected_set.add(v)

        # If the graph has too few edges or disconnected isolated nodes,
        # fill remaining slots by weighted degree.
        if len(selected_set) < k_variables:
            fallback = sorted(
                nodes,
                key=lambda node: (-_weighted_degree(qubo_graph, node), node),
            )

            for node in fallback:
                if len(selected_set) >= k_variables:
                    break
                selected_set.add(node)

        return sorted(selected_set)

    raise ValueError(f"Unknown sub-QUBO extraction strategy: {strategy}")


def extract_subqubo(
    qubo: Dict[str, Any],
    selected_variables: List[int],
    new_name_suffix: str | None = None,
) -> Dict[str, Any]:
    """
    Extract an induced sub-QUBO from the selected original variables.

    Variables are relabeled to 0..k-1.

    Example:
        selected_variables = [2, 5, 7]

    New variables:
        old 2 -> new 0
        old 5 -> new 1
        old 7 -> new 2

    Linear terms are kept for selected variables.
    Quadratic terms are kept only when both endpoints are selected.
    """
    n = int(qubo["n_variables"])
    selected = [int(v) for v in selected_variables]

    if len(selected) == 0:
        raise ValueError("selected_variables cannot be empty.")

    if len(set(selected)) != len(selected):
        raise ValueError("selected_variables contains duplicates.")

    if not set(selected).issubset(set(range(n))):
        raise ValueError("selected_variables must be valid original variable indices.")

    old_to_new = {
        old_var: new_idx
        for new_idx, old_var in enumerate(selected)
    }

    new_to_old = {
        new_idx: old_var
        for new_idx, old_var in enumerate(selected)
    }

    new_linear = {}

    for old_i in selected:
        new_i = old_to_new[old_i]
        new_linear[new_i] = float(qubo["linear"].get(old_i, 0.0))

    new_quadratic: Dict[Tuple[int, int], float] = {}

    selected_set = set(selected)

    for (old_i, old_j), value in qubo["quadratic"].items():
        old_i = int(old_i)
        old_j = int(old_j)

        if old_i in selected_set and old_j in selected_set:
            new_i = old_to_new[old_i]
            new_j = old_to_new[old_j]
            a, b = sorted((new_i, new_j))
            new_quadratic[(a, b)] = new_quadratic.get((a, b), 0.0) + float(value)

    suffix = "" if new_name_suffix is None else f"_{new_name_suffix}"

    subqubo = {
        "name": f"{qubo['name']}{suffix}",
        "family": qubo["family"],
        "n_variables": len(selected),
        "linear": new_linear,
        "quadratic": new_quadratic,
        "constant": float(qubo.get("constant", 0.0)),
        "metadata": dict(qubo.get("metadata", {})),
    }

    subqubo["metadata"]["subqubo_selected_original_variables"] = selected
    subqubo["metadata"]["subqubo_old_to_new"] = old_to_new
    subqubo["metadata"]["subqubo_new_to_old"] = new_to_old
    subqubo["metadata"]["subqubo_original_n_variables"] = n
    subqubo["metadata"]["subqubo_original_name"] = qubo["name"]

    return subqubo


def compute_interaction_preservation_metrics(
    qubo: Dict[str, Any],
    subqubo: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Compute basic interaction-preservation metrics.

    Metrics:
        variable_preservation_ratio
        edge_preservation_ratio
        weighted_edge_preservation_ratio

    Edge preservation is based on quadratic interactions retained in the
    induced sub-QUBO.

    Weighted edge preservation uses sum of absolute quadratic coefficients.
    """
    original_n = int(qubo["n_variables"])
    sub_n = int(subqubo["n_variables"])

    original_edges = qubo["quadratic"]
    sub_edges = subqubo["quadratic"]

    original_edge_count = len(original_edges)
    sub_edge_count = len(sub_edges)

    original_abs_weight = sum(abs(float(v)) for v in original_edges.values())
    sub_abs_weight = sum(abs(float(v)) for v in sub_edges.values())

    variable_preservation_ratio = sub_n / original_n

    if original_edge_count > 0:
        edge_preservation_ratio = sub_edge_count / original_edge_count
    else:
        edge_preservation_ratio = 0.0

    if original_abs_weight > 0:
        weighted_edge_preservation_ratio = sub_abs_weight / original_abs_weight
    else:
        weighted_edge_preservation_ratio = 0.0

    return {
        "original_n_variables": original_n,
        "sub_n_variables": sub_n,
        "original_n_edges": original_edge_count,
        "sub_n_edges": sub_edge_count,
        "variable_preservation_ratio": float(variable_preservation_ratio),
        "edge_preservation_ratio": float(edge_preservation_ratio),
        "original_abs_quadratic_weight": float(original_abs_weight),
        "sub_abs_quadratic_weight": float(sub_abs_weight),
        "weighted_edge_preservation_ratio": float(weighted_edge_preservation_ratio),
    }


def available_subqubo_strategies() -> List[str]:
    """
    Return currently implemented RQ3 sub-QUBO extraction strategies.
    """
    return [
        "top_weight_edges",
        "high_degree_nodes",
        "weighted_degree_nodes",
        "random_nodes",
    ]
