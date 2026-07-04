"""
Variable ordering and mapping strategies for RQ2.

RQ2 asks whether QUBO-graph-aware variable ordering and topology-aware
logical mapping can reduce transpilation overhead.

This first version implements only variable ordering strategies:

1. natural
2. random
3. degree_desc
4. weighted_degree_desc

The output is a list of logical variable indices in the order they should
be placed or considered.

Topology-aware physical placement will be added later.
"""

from __future__ import annotations

from typing import List
import numpy as np
import networkx as nx


def natural_ordering(graph: nx.Graph) -> List[int]:
    """
    Natural variable ordering:

        [0, 1, 2, ..., n-1]

    This is the baseline ordering.
    """
    return sorted(int(node) for node in graph.nodes())


def random_ordering(
    graph: nx.Graph,
    seed: int = 123,
) -> List[int]:
    """
    Random variable ordering with a fixed seed.

    This is used as a stochastic baseline.
    """
    nodes = natural_ordering(graph)

    rng = np.random.default_rng(seed)
    shuffled = list(nodes)
    rng.shuffle(shuffled)

    return shuffled


def degree_desc_ordering(graph: nx.Graph) -> List[int]:
    """
    Degree-descending ordering.

    Variables with more QUBO interactions are placed earlier.

    Tie-breaker:
        smaller variable index first.
    """
    return sorted(
        [int(node) for node in graph.nodes()],
        key=lambda node: (-graph.degree[node], node),
    )


def weighted_degree_desc_ordering(graph: nx.Graph) -> List[int]:
    """
    Weighted-degree-descending ordering.

    Weighted degree is the sum of absolute QUBO interaction weights incident
    to each variable.

    This captures not only how many interactions a variable has, but also
    how strong those interactions are.

    Tie-breaker:
        smaller variable index first.
    """
    def weighted_degree(node: int) -> float:
        total = 0.0

        for _, _, data in graph.edges(node, data=True):
            total += abs(float(data.get("weight", 1.0)))

        return total

    return sorted(
        [int(node) for node in graph.nodes()],
        key=lambda node: (-weighted_degree(node), node),
    )


def get_variable_ordering(
    graph: nx.Graph,
    strategy: str,
    seed: int = 123,
) -> List[int]:
    """
    Return variable ordering by strategy name.
    """
    if strategy == "natural":
        return natural_ordering(graph)

    if strategy == "random":
        return random_ordering(graph, seed=seed)

    if strategy == "degree_desc":
        return degree_desc_ordering(graph)

    if strategy == "weighted_degree_desc":
        return weighted_degree_desc_ordering(graph)

    raise ValueError(f"Unknown ordering strategy: {strategy}")


def available_ordering_strategies() -> List[str]:
    """
    Return currently implemented RQ2 ordering strategies.
    """
    return [
        "natural",
        "random",
        "degree_desc",
        "weighted_degree_desc",
    ]


def ordering_to_logical_layout(ordering: List[int]) -> dict[int, int]:
    """
    Convert an ordering into a logical-to-position map.

    Example:
        ordering = [5, 2, 0]

    means:
        variable 5 is placed at position 0
        variable 2 is placed at position 1
        variable 0 is placed at position 2

    Returns:
        {5: 0, 2: 1, 0: 2}

    This is not yet a physical-qubit layout.
    It is an ordering-position representation that later steps will use
    for topology-aware mapping.
    """
    return {
        int(variable): int(position)
        for position, variable in enumerate(ordering)
    }


def validate_ordering(graph: nx.Graph, ordering: List[int]) -> bool:
    """
    Check whether an ordering is a valid permutation of graph nodes.
    """
    graph_nodes = set(int(node) for node in graph.nodes())
    ordering_nodes = set(int(node) for node in ordering)

    if len(ordering) != graph.number_of_nodes():
        return False

    if graph_nodes != ordering_nodes:
        return False

    return True


def physical_qubit_ordering_by_topology(
    coupling_map,
    strategy: str = "centrality_desc",
) -> List[int]:
    """
    Return physical qubits ordered by topology desirability.

    centrality_desc ranks physical qubits by:
        1. degree, descending
        2. closeness centrality, descending
        3. physical qubit index, ascending
    """
    import networkx as nx

    topology_graph = nx.Graph()
    topology_graph.add_nodes_from(int(q) for q in coupling_map.physical_qubits)

    for u, v in coupling_map.get_edges():
        topology_graph.add_edge(int(u), int(v))

    if strategy != "centrality_desc":
        raise ValueError(f"Unknown physical topology ordering strategy: {strategy}")

    degree_dict = dict(topology_graph.degree())
    closeness_dict = nx.closeness_centrality(topology_graph)

    physical_order = sorted(
        [int(q) for q in topology_graph.nodes()],
        key=lambda q: (
            -degree_dict[q],
            -closeness_dict[q],
            q,
        ),
    )

    return physical_order


def build_topology_aware_initial_layout(
    n_qubits: int,
    coupling_map,
    physical_strategy: str = "centrality_desc",
) -> List[int]:
    """
    Build a topology-aware initial_layout list for Qiskit transpile.

    Assumption:
        The QUBO has already been relabeled by logical ordering.

    Then:
        circuit qubit 0 -> most central physical qubit
        circuit qubit 1 -> next most central physical qubit
        ...
    """
    physical_order = physical_qubit_ordering_by_topology(
        coupling_map=coupling_map,
        strategy=physical_strategy,
    )

    if len(physical_order) < n_qubits:
        raise ValueError("Coupling map has fewer physical qubits than circuit qubits.")

    return physical_order[:n_qubits]


def bfs_order_from_graph(
    graph: nx.Graph,
    start_node: int | None = None,
    weight_key: str | None = None,
) -> List[int]:
    """
    Create a BFS-style node ordering from a graph.

    If start_node is None, start from the highest-degree node.
    Ties are broken by smaller node index.

    Neighbor order:
        higher degree first, then smaller node index.

    This is intended to preserve local graph neighborhoods better than
    simple degree sorting.
    """
    if graph.number_of_nodes() == 0:
        return []

    nodes = [int(node) for node in graph.nodes()]

    if start_node is None:
        start_node = sorted(
            nodes,
            key=lambda node: (-graph.degree[node], node),
        )[0]

    visited = set()
    order = []
    queue = [int(start_node)]

    while queue:
        node = queue.pop(0)

        if node in visited:
            continue

        visited.add(node)
        order.append(node)

        neighbors = [
            int(neighbor)
            for neighbor in graph.neighbors(node)
            if int(neighbor) not in visited
        ]

        neighbors = sorted(
            neighbors,
            key=lambda neighbor: (-graph.degree[neighbor], neighbor),
        )

        for neighbor in neighbors:
            if neighbor not in visited and neighbor not in queue:
                queue.append(neighbor)

    # If the graph is disconnected, append remaining components.
    remaining = [node for node in nodes if node not in visited]

    while remaining:
        component_start = sorted(
            remaining,
            key=lambda node: (-graph.degree[node], node),
        )[0]

        queue = [component_start]

        while queue:
            node = queue.pop(0)

            if node in visited:
                continue

            visited.add(node)
            order.append(node)

            neighbors = [
                int(neighbor)
                for neighbor in graph.neighbors(node)
                if int(neighbor) not in visited
            ]

            neighbors = sorted(
                neighbors,
                key=lambda neighbor: (-graph.degree[neighbor], neighbor),
            )

            for neighbor in neighbors:
                if neighbor not in visited and neighbor not in queue:
                    queue.append(neighbor)

        remaining = [node for node in nodes if node not in visited]

    return order


def build_bfs_topology_aware_initial_layout(
    qubo_graph: nx.Graph,
    coupling_map,
) -> tuple[List[int], List[int], List[int]]:
    """
    Build BFS-based topology-aware layout.

    Returns
    -------
    qubo_ordering:
        Logical QUBO variables ordered by BFS from an important QUBO node.

    physical_ordering:
        Physical qubits ordered by BFS from a central topology node.

    initial_layout:
        Qiskit initial_layout list such that circuit qubit k is placed on
        physical_ordering[k].

    How to use
    ----------
    1. Relabel QUBO using qubo_ordering.
    2. Build QAOA circuit from relabeled QUBO.
    3. Transpile with initial_layout.
    """
    import networkx as nx

    # QUBO BFS ordering
    qubo_ordering = bfs_order_from_graph(qubo_graph)

    # Convert coupling map to topology graph
    topology_graph = nx.Graph()
    topology_graph.add_nodes_from(int(q) for q in coupling_map.physical_qubits)

    for u, v in coupling_map.get_edges():
        topology_graph.add_edge(int(u), int(v))

    # Start topology BFS from highest degree + highest closeness node
    degree_dict = dict(topology_graph.degree())
    closeness_dict = nx.closeness_centrality(topology_graph)

    topology_start = sorted(
        [int(q) for q in topology_graph.nodes()],
        key=lambda q: (-degree_dict[q], -closeness_dict[q], q),
    )[0]

    physical_ordering = bfs_order_from_graph(
        topology_graph,
        start_node=topology_start,
    )

    n_qubits = qubo_graph.number_of_nodes()

    if len(physical_ordering) < n_qubits:
        raise ValueError("Coupling map has fewer physical qubits than QUBO variables.")

    initial_layout = physical_ordering[:n_qubits]

    return qubo_ordering, physical_ordering, initial_layout
