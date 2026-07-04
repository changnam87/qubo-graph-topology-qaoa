"""
Topology-alignment descriptors for QUBO interaction graphs.

These descriptors measure how well a QUBO interaction graph aligns with
a target hardware coupling topology under a given logical-to-physical mapping.

For the current RQ1 extended analysis, we use natural mapping:

    logical variable i -> physical qubit i

RQ2 will later compare alternative mappings.
"""

from __future__ import annotations

from typing import Dict, Any, Tuple
import networkx as nx

from qiskit.transpiler import CouplingMap


def coupling_map_to_undirected_graph(coupling_map: CouplingMap) -> nx.Graph:
    """
    Convert a Qiskit CouplingMap into an undirected NetworkX graph.
    """
    graph = nx.Graph()

    physical_qubits = list(coupling_map.physical_qubits)
    graph.add_nodes_from(physical_qubits)

    for i, j in coupling_map.get_edges():
        graph.add_edge(int(i), int(j))

    return graph


def natural_mapping(n_variables: int) -> Dict[int, int]:
    """
    Natural logical-to-physical mapping:

        logical variable i -> physical qubit i
    """
    return {i: i for i in range(n_variables)}


def compute_topology_alignment_descriptors(
    qubo_graph: nx.Graph,
    coupling_map: CouplingMap,
    mapping: Dict[int, int] | None = None,
) -> Dict[str, Any]:
    """
    Compute topology-alignment descriptors for a QUBO interaction graph.

    Parameters
    ----------
    qubo_graph:
        NetworkX graph where nodes are QUBO variables and edges are QUBO
        quadratic interactions.

    coupling_map:
        Qiskit CouplingMap representing hardware connectivity.

    mapping:
        Dictionary from logical variable index to physical qubit index.
        If None, natural mapping is used.

    Returns
    -------
    descriptors:
        Dictionary of topology-alignment descriptors.
    """
    n_variables = qubo_graph.number_of_nodes()

    if mapping is None:
        mapping = natural_mapping(n_variables)

    topology_graph = coupling_map_to_undirected_graph(coupling_map)

    n_edges = qubo_graph.number_of_edges()

    if n_edges == 0:
        return {
            "topology_alignment_ratio": 0.0,
            "weighted_topology_alignment_ratio": 0.0,
            "mean_topology_distance": 0.0,
            "weighted_mean_topology_distance": 0.0,
            "max_topology_distance": 0.0,
            "n_aligned_edges": 0,
            "n_unaligned_edges": 0,
        }

    aligned_edges = 0
    unaligned_edges = 0

    total_abs_weight = 0.0
    aligned_abs_weight = 0.0

    distance_sum = 0.0
    weighted_distance_sum = 0.0
    max_distance = 0.0

    for u, v, data in qubo_graph.edges(data=True):
        physical_u = mapping[int(u)]
        physical_v = mapping[int(v)]

        abs_weight = abs(float(data.get("weight", 1.0)))
        total_abs_weight += abs_weight

        if topology_graph.has_edge(physical_u, physical_v):
            aligned_edges += 1
            aligned_abs_weight += abs_weight
            distance = 1.0
        else:
            unaligned_edges += 1

            try:
                distance = float(
                    nx.shortest_path_length(
                        topology_graph,
                        source=physical_u,
                        target=physical_v,
                    )
                )
            except nx.NetworkXNoPath:
                distance = float("inf")

        distance_sum += distance
        weighted_distance_sum += abs_weight * distance

        if distance > max_distance:
            max_distance = distance

    topology_alignment_ratio = aligned_edges / n_edges

    if total_abs_weight > 0:
        weighted_topology_alignment_ratio = aligned_abs_weight / total_abs_weight
        weighted_mean_topology_distance = weighted_distance_sum / total_abs_weight
    else:
        weighted_topology_alignment_ratio = 0.0
        weighted_mean_topology_distance = 0.0

    mean_topology_distance = distance_sum / n_edges

    return {
        "topology_alignment_ratio": float(topology_alignment_ratio),
        "weighted_topology_alignment_ratio": float(weighted_topology_alignment_ratio),
        "mean_topology_distance": float(mean_topology_distance),
        "weighted_mean_topology_distance": float(weighted_mean_topology_distance),
        "max_topology_distance": float(max_distance),
        "n_aligned_edges": int(aligned_edges),
        "n_unaligned_edges": int(unaligned_edges),
    }
