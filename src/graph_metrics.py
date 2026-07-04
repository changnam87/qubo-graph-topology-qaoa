"""
Graph descriptor extraction for QUBO interaction graphs.

These descriptors are used in RQ1 to explain QAOA circuit complexity
and transpilation overhead from QUBO graph structure.
"""

from __future__ import annotations

from typing import Dict, Any
import math

import numpy as np
import networkx as nx


def _safe_std(values) -> float:
    """Return population standard deviation, or 0.0 for empty input."""
    values = list(values)
    if len(values) == 0:
        return 0.0
    return float(np.std(values, ddof=0))


def _coefficient_entropy(abs_weights: np.ndarray) -> float:
    """
    Normalized Shannon entropy of absolute quadratic coefficients.

    Low value:
        one or a few interactions dominate.

    High value:
        interaction strength is spread more evenly across edges.
    """
    if abs_weights.size <= 1:
        return 0.0

    total = float(abs_weights.sum())
    if total <= 0:
        return 0.0

    probs = abs_weights / total
    entropy = -float(np.sum(probs * np.log(probs + 1e-15)))
    max_entropy = math.log(abs_weights.size)

    return float(entropy / max_entropy)


def _coefficient_concentration(abs_weights: np.ndarray) -> float:
    """
    Simple concentration metric:

        max absolute edge weight / sum absolute edge weights

    Near 1:
        one edge dominates.

    Smaller:
        weights are more distributed.
    """
    if abs_weights.size == 0:
        return 0.0

    total = float(abs_weights.sum())
    if total <= 0:
        return 0.0

    return float(abs_weights.max() / total)


def extract_graph_descriptors(graph: nx.Graph) -> Dict[str, Any]:
    """
    Extract graph-level descriptors from a QUBO interaction graph.
    """
    n = graph.number_of_nodes()
    m = graph.number_of_edges()

    possible_edges = n * (n - 1) / 2
    density = 0.0 if possible_edges == 0 else m / possible_edges

    degrees = np.array(
        [degree for _, degree in graph.degree()],
        dtype=float,
    )

    weighted_degrees = np.array(
        [
            sum(
                abs(data.get("weight", 0.0))
                for _, _, data in graph.edges(node, data=True)
            )
            for node in graph.nodes()
        ],
        dtype=float,
    )

    edge_weights = np.array(
        [
            data.get("weight", 0.0)
            for _, _, data in graph.edges(data=True)
        ],
        dtype=float,
    )

    abs_edge_weights = np.abs(edge_weights)

    if n > 0:
        components = list(nx.connected_components(graph))
        connected_components = len(components)
        largest_component_size = max(len(c) for c in components)
    else:
        connected_components = 0
        largest_component_size = 0

    if m > 0:
        communities = list(
            nx.algorithms.community.greedy_modularity_communities(
                graph,
                weight="abs_weight",
            )
        )
        community_count = len(communities)
        modularity = nx.algorithms.community.modularity(
            graph,
            communities,
            weight="abs_weight",
        )
    else:
        community_count = n
        modularity = 0.0

    return {
        "instance_name": graph.graph.get("name", "unknown"),
        "family": graph.graph.get("family", "unknown"),

        "n_variables": n,
        "n_edges": m,
        "density": float(density),

        "avg_degree": float(degrees.mean()) if degrees.size else 0.0,
        "max_degree": float(degrees.max()) if degrees.size else 0.0,
        "degree_std": _safe_std(degrees),

        "weighted_degree_mean": float(weighted_degrees.mean()) if weighted_degrees.size else 0.0,
        "weighted_degree_max": float(weighted_degrees.max()) if weighted_degrees.size else 0.0,
        "weighted_degree_std": _safe_std(weighted_degrees),

        "quadratic_coeff_min": float(edge_weights.min()) if edge_weights.size else 0.0,
        "quadratic_coeff_max": float(edge_weights.max()) if edge_weights.size else 0.0,
        "quadratic_coeff_abs_mean": float(abs_edge_weights.mean()) if abs_edge_weights.size else 0.0,
        "quadratic_coeff_abs_max": float(abs_edge_weights.max()) if abs_edge_weights.size else 0.0,
        "quadratic_coeff_range": float(edge_weights.max() - edge_weights.min()) if edge_weights.size else 0.0,

        "coefficient_entropy": _coefficient_entropy(abs_edge_weights),
        "coefficient_concentration": _coefficient_concentration(abs_edge_weights),

        "connected_components": connected_components,
        "largest_component_size": largest_component_size,

        "community_count": int(community_count),
        "modularity": float(modularity),
    }
