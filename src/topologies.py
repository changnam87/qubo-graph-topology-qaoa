"""
Local topology definitions for RQ1 transpilation experiments.

No hardware API calls are used.

Each topology is represented as a Qiskit CouplingMap.
These coupling maps will later be used for topology-aware transpilation.
"""

from __future__ import annotations

from typing import Dict, List, Tuple
import math

from qiskit.transpiler import CouplingMap


EdgeList = List[Tuple[int, int]]


def _make_bidirectional_edges(edges: EdgeList) -> EdgeList:
    """
    Convert an undirected edge list into a directed bidirectional edge list.

    Qiskit CouplingMap uses directed edges.
    For this pilot, we assume gates can be routed in both directions.
    """
    directed = []

    for i, j in edges:
        directed.append((i, j))
        directed.append((j, i))

    return directed


def line_coupling_map(n_qubits: int) -> CouplingMap:
    """
    Create a line topology:

        0 -- 1 -- 2 -- ... -- n-1
    """
    if n_qubits < 2:
        raise ValueError("line topology needs at least 2 qubits.")

    edges = [(i, i + 1) for i in range(n_qubits - 1)]
    return CouplingMap(_make_bidirectional_edges(edges))


def fully_connected_coupling_map(n_qubits: int) -> CouplingMap:
    """
    Create a fully connected reference topology.

    Every qubit can directly interact with every other qubit.
    """
    if n_qubits < 2:
        raise ValueError("fully connected topology needs at least 2 qubits.")

    edges = []

    for i in range(n_qubits):
        for j in range(i + 1, n_qubits):
            edges.append((i, j))

    return CouplingMap(_make_bidirectional_edges(edges))


def grid_2d_coupling_map(n_qubits: int) -> CouplingMap:
    """
    Create an approximately square 2D grid topology.

    For example, n_qubits = 16 becomes a 4 x 4 grid.

    If n_qubits is not a perfect square, the grid is filled row by row.
    """
    if n_qubits < 2:
        raise ValueError("2D grid topology needs at least 2 qubits.")

    n_cols = math.ceil(math.sqrt(n_qubits))
    n_rows = math.ceil(n_qubits / n_cols)

    def node_id(row: int, col: int) -> int:
        return row * n_cols + col

    edges = []

    for row in range(n_rows):
        for col in range(n_cols):
            current = node_id(row, col)

            if current >= n_qubits:
                continue

            right = node_id(row, col + 1)
            down = node_id(row + 1, col)

            if col + 1 < n_cols and right < n_qubits:
                edges.append((current, right))

            if row + 1 < n_rows and down < n_qubits:
                edges.append((current, down))

    return CouplingMap(_make_bidirectional_edges(edges))


def heavy_hex_like_coupling_map(n_qubits: int) -> CouplingMap:
    """
    Create a simple sparse hardware-like topology.

    This is not an exact IBM heavy-hex device layout.
    It is a lightweight local approximation for pilot experiments.

    Design idea:
    - Start with a line backbone.
    - Add sparse skip connections every few qubits.
    - Keep connectivity sparse relative to fully connected topology.

    This gives a hardware-like sparse graph without calling any hardware API.
    """
    if n_qubits < 2:
        raise ValueError("heavy-hex-like topology needs at least 2 qubits.")

    edges = set()

    # Backbone line
    for i in range(n_qubits - 1):
        edges.add((i, i + 1))

    # Sparse skip links
    for i in range(0, n_qubits - 2, 3):
        edges.add((i, i + 2))

    # Additional staggered sparse links
    for i in range(1, n_qubits - 3, 4):
        edges.add((i, i + 3))

    clean_edges = sorted(edges)
    return CouplingMap(_make_bidirectional_edges(clean_edges))


def get_coupling_map(topology_name: str, n_qubits: int) -> CouplingMap:
    """
    Return a CouplingMap by topology name.
    """
    if topology_name == "line":
        return line_coupling_map(n_qubits)

    if topology_name == "grid_2d":
        return grid_2d_coupling_map(n_qubits)

    if topology_name == "heavy_hex_like":
        return heavy_hex_like_coupling_map(n_qubits)

    if topology_name == "fully_connected":
        return fully_connected_coupling_map(n_qubits)

    raise ValueError(f"Unknown topology_name: {topology_name}")


def available_topologies() -> List[str]:
    """
    Return the topology names used in the RQ1 pilot.
    """
    return [
        "line",
        "grid_2d",
        "heavy_hex_like",
        "fully_connected",
    ]


def coupling_map_summary(topology_name: str, n_qubits: int) -> Dict[str, int | str | bool]:
    """
    Return a small summary of a coupling map.
    """
    cmap = get_coupling_map(topology_name, n_qubits)

    directed_edges = cmap.get_edges()
    undirected_edges = {
        tuple(sorted((int(i), int(j))))
        for i, j in directed_edges
        if int(i) != int(j)
    }

    return {
        "topology": topology_name,
        "n_qubits": n_qubits,
        "n_directed_edges": len(directed_edges),
        "n_undirected_edges": len(undirected_edges),
        "is_connected": cmap.is_connected(),
    }
