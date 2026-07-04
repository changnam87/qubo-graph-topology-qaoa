"""
RQ2 mapping evaluation helper.

This module converts a high-level RQ2 mapping strategy name into:

1. relabeled QUBO
2. initial_layout for Qiskit transpile
3. ordering metadata
4. layout metadata

It centralizes RQ2 strategy logic so experiment scripts remain clean.
"""

from __future__ import annotations

from typing import Dict, Any, List
import networkx as nx

from qiskit.transpiler import CouplingMap

from src.mapping_strategies import (
    natural_ordering,
    random_ordering,
    degree_desc_ordering,
    weighted_degree_desc_ordering,
    build_topology_aware_initial_layout,
    build_bfs_topology_aware_initial_layout,
)
from src.qubo_relabeling import relabel_qubo_by_ordering


RQ2_STRATEGIES = [
    "standard_qiskit",
    "natural_fixed",
    "random_fixed",
    "degree_desc_fixed",
    "weighted_degree_desc_fixed",
    "degree_desc_centrality_layout",
    "weighted_degree_desc_centrality_layout",
    "bfs_topology_aware",
]


def available_rq2_strategies() -> List[str]:
    """
    Return final RQ2 strategy names.
    """
    return list(RQ2_STRATEGIES)


def prepare_rq2_mapping_condition(
    qubo: Dict[str, Any],
    qubo_graph: nx.Graph,
    coupling_map: CouplingMap,
    strategy_name: str,
    random_seed: int = 123,
) -> Dict[str, Any]:
    """
    Prepare one RQ2 mapping condition.

    Parameters
    ----------
    qubo:
        Original QUBO dictionary.

    qubo_graph:
        Interaction graph of the original QUBO.

    coupling_map:
        Target topology.

    strategy_name:
        One of:
            standard_qiskit
            natural_fixed
            random_fixed
            degree_desc_fixed
            weighted_degree_desc_fixed
            degree_desc_centrality_layout
            weighted_degree_desc_centrality_layout
            bfs_topology_aware

    random_seed:
        Seed for random ordering.

    Returns
    -------
    condition:
        Dictionary containing:
            - relabeled_qubo
            - initial_layout
            - ordering_used
            - physical_ordering_used
            - layout_mode
            - strategy_name
    """
    n = int(qubo["n_variables"])

    if strategy_name == "standard_qiskit":
        ordering = natural_ordering(qubo_graph)
        relabeled_qubo = relabel_qubo_by_ordering(
            qubo,
            ordering=ordering,
            new_name_suffix="standard_qiskit",
        )

        return {
            "strategy_name": strategy_name,
            "layout_mode": "standard_qiskit",
            "relabeling_mode": "natural",
            "relabeled_qubo": relabeled_qubo,
            "initial_layout": None,
            "ordering_used": ordering,
            "physical_ordering_used": None,
        }

    if strategy_name == "natural_fixed":
        ordering = natural_ordering(qubo_graph)
        relabeled_qubo = relabel_qubo_by_ordering(
            qubo,
            ordering=ordering,
            new_name_suffix="natural_fixed",
        )

        return {
            "strategy_name": strategy_name,
            "layout_mode": "fixed_identity_after_relabeling",
            "relabeling_mode": "natural",
            "relabeled_qubo": relabeled_qubo,
            "initial_layout": list(range(n)),
            "ordering_used": ordering,
            "physical_ordering_used": list(range(n)),
        }

    if strategy_name == "random_fixed":
        ordering = random_ordering(
            qubo_graph,
            seed=random_seed,
        )
        relabeled_qubo = relabel_qubo_by_ordering(
            qubo,
            ordering=ordering,
            new_name_suffix="random_fixed",
        )

        return {
            "strategy_name": strategy_name,
            "layout_mode": "fixed_identity_after_relabeling",
            "relabeling_mode": "random",
            "relabeled_qubo": relabeled_qubo,
            "initial_layout": list(range(n)),
            "ordering_used": ordering,
            "physical_ordering_used": list(range(n)),
        }

    if strategy_name == "degree_desc_fixed":
        ordering = degree_desc_ordering(qubo_graph)
        relabeled_qubo = relabel_qubo_by_ordering(
            qubo,
            ordering=ordering,
            new_name_suffix="degree_desc_fixed",
        )

        return {
            "strategy_name": strategy_name,
            "layout_mode": "fixed_identity_after_relabeling",
            "relabeling_mode": "degree_desc",
            "relabeled_qubo": relabeled_qubo,
            "initial_layout": list(range(n)),
            "ordering_used": ordering,
            "physical_ordering_used": list(range(n)),
        }

    if strategy_name == "weighted_degree_desc_fixed":
        ordering = weighted_degree_desc_ordering(qubo_graph)
        relabeled_qubo = relabel_qubo_by_ordering(
            qubo,
            ordering=ordering,
            new_name_suffix="weighted_degree_desc_fixed",
        )

        return {
            "strategy_name": strategy_name,
            "layout_mode": "fixed_identity_after_relabeling",
            "relabeling_mode": "weighted_degree_desc",
            "relabeled_qubo": relabeled_qubo,
            "initial_layout": list(range(n)),
            "ordering_used": ordering,
            "physical_ordering_used": list(range(n)),
        }

    if strategy_name == "degree_desc_centrality_layout":
        ordering = degree_desc_ordering(qubo_graph)
        relabeled_qubo = relabel_qubo_by_ordering(
            qubo,
            ordering=ordering,
            new_name_suffix="degree_desc_centrality_layout",
        )

        initial_layout = build_topology_aware_initial_layout(
            n_qubits=n,
            coupling_map=coupling_map,
            physical_strategy="centrality_desc",
        )

        return {
            "strategy_name": strategy_name,
            "layout_mode": "topology_aware_centrality",
            "relabeling_mode": "degree_desc",
            "relabeled_qubo": relabeled_qubo,
            "initial_layout": initial_layout,
            "ordering_used": ordering,
            "physical_ordering_used": initial_layout,
        }

    if strategy_name == "weighted_degree_desc_centrality_layout":
        ordering = weighted_degree_desc_ordering(qubo_graph)
        relabeled_qubo = relabel_qubo_by_ordering(
            qubo,
            ordering=ordering,
            new_name_suffix="weighted_degree_desc_centrality_layout",
        )

        initial_layout = build_topology_aware_initial_layout(
            n_qubits=n,
            coupling_map=coupling_map,
            physical_strategy="centrality_desc",
        )

        return {
            "strategy_name": strategy_name,
            "layout_mode": "topology_aware_centrality",
            "relabeling_mode": "weighted_degree_desc",
            "relabeled_qubo": relabeled_qubo,
            "initial_layout": initial_layout,
            "ordering_used": ordering,
            "physical_ordering_used": initial_layout,
        }

    if strategy_name == "bfs_topology_aware":
        qubo_ordering, physical_ordering, initial_layout = (
            build_bfs_topology_aware_initial_layout(
                qubo_graph=qubo_graph,
                coupling_map=coupling_map,
            )
        )

        relabeled_qubo = relabel_qubo_by_ordering(
            qubo,
            ordering=qubo_ordering,
            new_name_suffix="bfs_topology_aware",
        )

        return {
            "strategy_name": strategy_name,
            "layout_mode": "bfs_topology_aware",
            "relabeling_mode": "bfs_graph_order",
            "relabeled_qubo": relabeled_qubo,
            "initial_layout": initial_layout,
            "ordering_used": qubo_ordering,
            "physical_ordering_used": physical_ordering,
        }

    raise ValueError(f"Unknown RQ2 strategy: {strategy_name}")
